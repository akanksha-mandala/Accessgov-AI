import logging
import os
from typing import Optional

from sqlalchemy.orm import Session

from schemas.document import DocumentAnalysisResponse

import crud.crud_document as crud_document

from models.uploaded_documents import VerificationStatus

from document_intelligence.ocr_engine import ocr_engine
from document_intelligence.document_classifier import document_classifier
from document_intelligence.field_extractors import field_extractor_engine
from document_intelligence.validators import document_validator
from document_intelligence.readiness_engine import document_readiness_engine


logger = logging.getLogger(
    "accessgov.services.document_service"
)


class DocumentService:
    """
    Master Document Intelligence Orchestration Service.

    Pipeline:

        Storage
          ↓
        OCR
          ↓
        Classification
          ↓
        Field Extraction
          ↓
        Validation
          ↓
        Readiness Calculation
          ↓
        Database Persistence
          ↓
        Reusable Personal Vault

    Important behavior:

    - OCR metrics always come from the actual OCR engine.
    - OCR failures are retained as PENDING.
    - Successfully inspected documents are retained.
    - Documents meeting the automatic reusable threshold are marked
      VERIFIED.
    - Documents below that threshold remain PENDING.
    - No document is deleted merely because automated inspection fails.
    - Explanation generation is non-critical: failure to generate an
      explanation must never prevent OCR results from being persisted.
    """

    @staticmethod
    def _discard_uploaded_file(file_path: str) -> None:
        """
        Compatibility helper.

        Uploaded documents are intentionally retained even when
        automated inspection fails.
        """
        try:
            if file_path and os.path.isfile(file_path):
                os.remove(file_path)

                logger.info(
                    "Discarded uploaded document: %s",
                    file_path,
                )

        except Exception:
            logger.exception(
                "Failed to remove uploaded file: %s",
                file_path,
            )

    @staticmethod
    def _fallback_explanation(
        document_type: str,
        readiness_result,
        validation_result,
    ) -> str:
        """
        Deterministic fallback explanation.

        This is deliberately local and does not call an external
        language model. It guarantees that explanation generation
        cannot block document persistence.
        """

        missing_fields = list(
            getattr(validation_result, "missing_fields", [])
            or []
        )

        warnings = list(
            getattr(validation_result, "warnings", [])
            or []
        )

        readiness_score = float(
            getattr(
                readiness_result,
                "readiness_score",
                0.0,
            )
            or 0.0
        )

        if missing_fields:
            missing_text = ", ".join(
                str(item)
                for item in missing_fields
            )

            return (
                f"The document was identified as {document_type}. "
                f"Automated inspection completed, but the following "
                f"required information could not be confirmed: "
                f"{missing_text}. "
                f"Current readiness score: {readiness_score:.1f}/100."
            )

        if warnings:
            warning_text = "; ".join(
                str(item)
                for item in warnings
            )

            return (
                f"The document was identified as {document_type}. "
                f"Automated inspection completed with the following "
                f"warning(s): {warning_text}. "
                f"Current readiness score: {readiness_score:.1f}/100."
            )

        return (
            f"The document was identified as {document_type}. "
            f"Automated OCR and document inspection completed "
            f"successfully. Current readiness score: "
            f"{readiness_score:.1f}/100."
        )

    @staticmethod
    def analyze_document_file(
        db: Session,
        user_id: int,
        file_path: str,
        original_file_name: str,
        mime_type: str,
        file_size_bytes: int,
        language: str = "en",
        application_id: Optional[int] = None,
        selected_document_type: str = "Government Document",
    ) -> DocumentAnalysisResponse:

        # ============================================================
        # NORMALIZE SELECTED DOCUMENT TYPE
        # ============================================================

        selected_document_type = (
            selected_document_type.strip()
            if selected_document_type
            else "Government Document"
        )

        logger.info(
            "DOCUMENT ANALYSIS START | file=%s | user_id=%s | "
            "selected_type=%s | mime=%s | size=%s",
            original_file_name,
            user_id,
            selected_document_type,
            mime_type,
            file_size_bytes,
        )

        # ============================================================
        # 1. OCR TEXT EXTRACTION
        # ============================================================

        logger.info(
            "DOCUMENT ANALYSIS STAGE 1/7 | OCR START | file=%s",
            original_file_name,
        )

        try:
            ocr_res = ocr_engine.process_document(
                file_path=file_path,
                mime_type=mime_type,
            )
        except Exception as exc:
            logger.exception(
                "DOCUMENT ANALYSIS | OCR ENGINE EXCEPTION | file=%s",
                original_file_name,
            )

            raise RuntimeError(
                f"OCR processing failed for '{original_file_name}': "
                f"{exc}"
            ) from exc

        logger.info(
            "DOCUMENT ANALYSIS STAGE 1/7 | OCR COMPLETE | file=%s | "
            "status=%s | confidence=%.4f | readability=%.2f | "
            "sharpness=%.2f | pages=%s",
            original_file_name,
            ocr_res.status,
            float(ocr_res.confidence or 0),
            float(ocr_res.readability_score or 0),
            float(ocr_res.sharpness_score or 0),
            getattr(ocr_res, "page_count", 0),
        )

        # ============================================================
        # 2. OCR FAILURE
        # ============================================================

        if ocr_res.status != "success":

            logger.warning(
                "DOCUMENT ANALYSIS | OCR FAILED | file=%s | "
                "status=%s | error=%s",
                original_file_name,
                ocr_res.status,
                ocr_res.error_message,
            )

            validation_result = (
                document_validator.validate_extracted_fields(
                    selected_document_type,
                    {},
                    0.0,
                )
            )

            readiness = (
                document_readiness_engine.calculate_readiness(
                    document_type=selected_document_type,
                    extracted_fields={},
                    validation_result=validation_result,
                    ocr_confidence=0.0,
                )
            )

            explanation_text = (
                ocr_res.error_message
                or (
                    "The document could not be read by automated OCR. "
                    "It has been saved to your Personal Vault as "
                    "pending so that it can be reviewed or re-analyzed."
                )
            )

            logger.info(
                "DOCUMENT ANALYSIS | PERSISTING OCR FAILURE | file=%s",
                original_file_name,
            )

            db_doc = crud_document.create_document_record(
                db=db,
                user_id=user_id,
                file_name=original_file_name,
                file_path=file_path,
                mime_type=mime_type,
                file_size_bytes=file_size_bytes,
                document_type=selected_document_type,
                application_id=application_id,
                ocr_status=ocr_res.status,
                ocr_confidence=ocr_res.confidence,
                readability_score=ocr_res.readability_score,
                sharpness_score=ocr_res.sharpness_score,
                readiness_score=readiness.readiness_score,
                quality_issues=ocr_res.quality_issues,
                extracted_fields={},
                validation_errors=(
                    validation_result.missing_fields
                    + validation_result.warnings
                ),
            )

            crud_document.update_document_status(
                db,
                db_doc.id,
                status=VerificationStatus.PENDING,
            )

            logger.info(
                "DOCUMENT ANALYSIS COMPLETE | OCR FAILURE RETAINED | "
                "file=%s | document_id=%s",
                original_file_name,
                db_doc.id,
            )

            return DocumentAnalysisResponse(
                document_id=db_doc.id,
                file_name=original_file_name,
                document_type=selected_document_type,
                classification_confidence=0.0,
                ocr_result=ocr_res,
                extracted_fields={},
                validation_result=validation_result,
                readiness_result=readiness,
                explanation=explanation_text,
            )

        # ============================================================
        # 3. DOCUMENT CLASSIFICATION
        # ============================================================

        logger.info(
            "DOCUMENT ANALYSIS STAGE 2/7 | CLASSIFICATION START | "
            "file=%s",
            original_file_name,
        )

        doc_type, class_conf, matched_indicators = (
            document_classifier.classify_text(
                ocr_res.raw_text
            )
        )

        if not doc_type or doc_type == "Unknown Document":
            doc_type = selected_document_type

        logger.info(
            "DOCUMENT ANALYSIS STAGE 2/7 | CLASSIFICATION COMPLETE | "
            "file=%s | type=%s | confidence=%.4f | indicators=%s",
            original_file_name,
            doc_type,
            float(class_conf or 0),
            matched_indicators,
        )

        # ============================================================
        # 4. FIELD EXTRACTION
        # ============================================================

        logger.info(
            "DOCUMENT ANALYSIS STAGE 3/7 | FIELD EXTRACTION START | "
            "file=%s",
            original_file_name,
        )

        extracted_fields = (
            field_extractor_engine.extract_fields(
                doc_type,
                ocr_res.raw_text,
            )
        )

        logger.info(
            "DOCUMENT ANALYSIS STAGE 3/7 | FIELD EXTRACTION COMPLETE | "
            "file=%s | fields=%s",
            original_file_name,
            list(extracted_fields.keys())
            if isinstance(extracted_fields, dict)
            else "non-dict-result",
        )

        # ============================================================
        # 5. FIELD VALIDATION
        # ============================================================

        logger.info(
            "DOCUMENT ANALYSIS STAGE 4/7 | VALIDATION START | file=%s",
            original_file_name,
        )

        val_res = (
            document_validator.validate_extracted_fields(
                document_type=doc_type,
                fields=extracted_fields,
                ocr_confidence=ocr_res.confidence,
            )
        )

        logger.info(
            "DOCUMENT ANALYSIS STAGE 4/7 | VALIDATION COMPLETE | "
            "file=%s | valid=%s | missing=%s | warnings=%s",
            original_file_name,
            val_res.is_valid,
            val_res.missing_fields,
            val_res.warnings,
        )

        # ============================================================
        # 6. READINESS CALCULATION
        # ============================================================

        logger.info(
            "DOCUMENT ANALYSIS STAGE 5/7 | READINESS START | file=%s",
            original_file_name,
        )

        readiness_res = (
            document_readiness_engine.calculate_readiness(
                document_type=doc_type,
                extracted_fields=extracted_fields,
                validation_result=val_res,
                ocr_confidence=ocr_res.confidence,
            )
        )

        logger.info(
            "DOCUMENT ANALYSIS STAGE 5/7 | READINESS COMPLETE | "
            "file=%s | score=%.2f",
            original_file_name,
            float(
                readiness_res.readiness_score or 0
            ),
        )

        # ============================================================
        # 7. DETERMINE REUSABILITY
        # ============================================================

        document_accepted = (
            ocr_res.status == "success"
            and doc_type != "Unknown Document"
            and val_res.is_valid
            and readiness_res.readiness_score >= 80.0
        )

        # ============================================================
        # 8. PERSIST ANALYSIS RESULT
        #
        # IMPORTANT:
        # Persistence happens BEFORE explanation generation.
        #
        # Therefore an explanation problem can never cause a
        # successfully completed OCR analysis to disappear.
        # ============================================================

        logger.info(
            "DOCUMENT ANALYSIS STAGE 6/7 | DATABASE PERSIST START | "
            "file=%s | accepted=%s",
            original_file_name,
            document_accepted,
        )

        db_doc = crud_document.create_document_record(
            db=db,
            user_id=user_id,
            file_name=original_file_name,
            file_path=file_path,
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
            document_type=doc_type,
            application_id=application_id,
            ocr_status=ocr_res.status,
            ocr_confidence=ocr_res.confidence,
            readability_score=ocr_res.readability_score,
            sharpness_score=ocr_res.sharpness_score,
            readiness_score=readiness_res.readiness_score,
            quality_issues=ocr_res.quality_issues,
            extracted_fields=extracted_fields,
            validation_errors=(
                val_res.missing_fields
                + val_res.warnings
            ),
        )

        if document_accepted:
            crud_document.update_document_status(
                db,
                db_doc.id,
                status=VerificationStatus.VERIFIED,
            )

            logger.info(
                "DOCUMENT ANALYSIS | DATABASE STATUS=VERIFIED | "
                "document_id=%s | readiness=%.2f",
                db_doc.id,
                float(
                    readiness_res.readiness_score or 0
                ),
            )

        else:
            crud_document.update_document_status(
                db,
                db_doc.id,
                status=VerificationStatus.PENDING,
            )

            logger.info(
                "DOCUMENT ANALYSIS | DATABASE STATUS=PENDING | "
                "document_id=%s | readiness=%.2f | validation=%s",
                db_doc.id,
                float(
                    readiness_res.readiness_score or 0
                ),
                val_res.is_valid,
            )

        logger.info(
            "DOCUMENT ANALYSIS STAGE 6/7 | DATABASE PERSIST COMPLETE | "
            "file=%s | document_id=%s",
            original_file_name,
            db_doc.id,
        )

        # ============================================================
        # 9. EXPLANATION
        #
        # IMPORTANT:
        # Do NOT call an external/LLM explainer here.
        #
        # OCR, extraction, validation and readiness are already
        # complete and persisted. The upload endpoint must return
        # immediately with those real results.
        # ============================================================

        logger.info(
            "DOCUMENT ANALYSIS STAGE 7/7 | "
            "DETERMINISTIC EXPLANATION | file=%s",
            original_file_name,
        )

        explanation_text = (
            DocumentService._fallback_explanation(
                document_type=doc_type,
                readiness_result=readiness_res,
                validation_result=val_res,
            )
        )

        if not document_accepted:
            explanation_text = (
                f"{explanation_text} "
                "The document has been saved to your Personal Vault "
                "for review because it did not yet meet the automatic "
                "reusable-document threshold."
            )

        logger.info(
            "DOCUMENT ANALYSIS COMPLETE | file=%s | document_id=%s | "
            "ocr_status=%s | readiness=%.2f",
            original_file_name,
            db_doc.id,
            ocr_res.status,
            float(
                readiness_res.readiness_score or 0
            ),
        )

        # ============================================================
        # 10. RETURN REAL ANALYSIS
        # ============================================================

        return DocumentAnalysisResponse(
            document_id=db_doc.id,
            file_name=original_file_name,
            document_type=doc_type,
            classification_confidence=class_conf,
            ocr_result=ocr_res,
            extracted_fields=extracted_fields,
            validation_result=val_res,
            readiness_result=readiness_res,
            explanation=explanation_text,
        )


document_service = DocumentService()