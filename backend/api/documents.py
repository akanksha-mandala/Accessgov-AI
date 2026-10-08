from typing import List, Optional, Dict

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
    Query,
)

from sqlalchemy.orm import Session

from database import get_db

from models.users import User, UserRole
from models.uploaded_documents import UploadedDocument, VerificationStatus

from schemas.document import (
    DocumentUploadResponse,
    DocumentAnalysisResponse,
)

from schemas.common import MessageResponse

from auth.dependencies import get_current_active_user

import crud.crud_document as crud_document

from utils.file_storage import file_storage_util

from services.document_service import document_service


router = APIRouter(
    prefix="/documents",
    tags=["Document Intelligence & Uploads"],
)


# ============================================================
# CITIZEN DOCUMENT UPLOAD + ANALYSIS
# ============================================================

@router.post(
    "/upload",
    response_model=DocumentAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and analyze a government document (Authenticated Citizens)",
)
def upload_and_analyze_document(
    file: UploadFile = File(
        ...,
        description="Document file: PDF, PNG, JPG, JPEG (Max 10MB)",
    ),
    document_type: str = Form(
        "Government Document",
        description="User-selected document type",
    ),
    language: str = Form(
        "en",
        description="Preferred response language",
    ),
    application_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    POST /api/v1/documents/upload

    Uploads a citizen document, validates size and format,
    securely stores the file, runs the document intelligence
    pipeline, and returns the analysis result.
    """

    normalized_document_type = document_type.strip().casefold()

    existing_documents = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.user_id == current_user.id,
            UploadedDocument.verification_status
            != VerificationStatus.REJECTED,
        )
        .all()
    )

    duplicate_document = next(
        (
            doc
            for doc in existing_documents
            if (doc.document_type or "").strip().casefold()
            == normalized_document_type
        ),
        None,
    )

    if duplicate_document:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"You already have an active "
                f"'{duplicate_document.document_type}' "
                "in your Personal Vault. "
                "Delete the existing document before uploading "
                "a replacement."
            ),
        )

    saved_path, unique_filename, file_size, mime_type = (
        file_storage_util.validate_and_save_upload(file)
    )

    analysis_res = document_service.analyze_document_file(
        db=db,
        user_id=current_user.id,
        file_path=saved_path,
        original_file_name=file.filename or unique_filename,
        mime_type=mime_type,
        file_size_bytes=file_size,
        language=language,
        application_id=application_id,
        selected_document_type=document_type,
    )

    return analysis_res


# ============================================================
# CITIZEN DOCUMENT LIST
# ============================================================

@router.get(
    "/me",
    response_model=List[DocumentUploadResponse],
    status_code=status.HTTP_200_OK,
    summary="List citizen's uploaded documents",
)
def get_user_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    GET /api/v1/documents/me

    Retrieves documents belonging to the authenticated citizen.

    OCR, readability, quality, extraction, validation, and
    readiness values are read from the persisted database record.
    OCR is NOT re-run when the vault is opened.
    """

    docs = crud_document.list_user_documents(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

    enriched = []

    for doc in docs:
        persisted_confidence = (
            float(doc.ocr_confidence) * 100
            if doc.ocr_confidence is not None
            else 0
        )

        item = {
            "id": doc.id,
            "document_type": doc.document_type,
            "file_name": doc.file_name,
            "mime_type": doc.mime_type,
            "file_size_bytes": doc.file_size_bytes,
            "verification_status": doc.verification_status,
            "uploaded_at": doc.uploaded_at,
            "readiness_score": (
                float(doc.readiness_score)
                if doc.readiness_score is not None
                else 0
            ),
            "readability_score": (
                float(doc.readability_score)
                if doc.readability_score is not None
                else 0
            ),
            "ocr_confidence": persisted_confidence,
            "sharpness_score": (
                float(doc.sharpness_score)
                if doc.sharpness_score is not None
                else 0
            ),
            "quality_issues": doc.quality_issues or [],
            "ocr_status": doc.ocr_status or "not_analyzed",
            "extracted_fields": doc.extracted_fields or {},
            "validation_errors": doc.validation_errors or [],
        }

        enriched.append(item)

    return enriched


# ============================================================
# ADMIN DOCUMENT ANALYTICS
# ============================================================

@router.get(
    "/admin/analytics",
    status_code=status.HTTP_200_OK,
    summary="Anonymous aggregate document analytics for administrators",
)
def get_document_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    GET /api/v1/documents/admin/analytics

    Returns aggregate document statistics directly from
    persisted PostgreSQL document-intelligence results.

    Administrators receive aggregate information only.
    Individual document files and personal document contents
    are never returned by this endpoint.
    """

    # ========================================================
    # 1. Verify administrator access
    # ========================================================

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required.",
        )

    # ========================================================
    # 2. Read persisted document records
    # ========================================================

    docs = (
        db.query(UploadedDocument)
        .order_by(UploadedDocument.uploaded_at.desc())
        .all()
    )

    total = len(docs)

    # ========================================================
    # 3. Verification status statistics
    # ========================================================

    verified = sum(
        1
        for doc in docs
        if doc.verification_status
        == VerificationStatus.VERIFIED
    )

    pending = sum(
        1
        for doc in docs
        if doc.verification_status
        == VerificationStatus.PENDING
    )

    rejected = sum(
        1
        for doc in docs
        if doc.verification_status
        == VerificationStatus.REJECTED
    )

    # ========================================================
    # 4. OCR success statistics
    #
    # Different versions of the document pipeline may persist
    # different successful OCR status strings. Do not rely on
    # exactly one literal value.
    #
    # If the status is not one of the known successful values,
    # persisted OCR quality fields are used as a fallback.
    # ========================================================

    successful_ocr_statuses = {
        "success",
        "successful",
        "completed",
        "complete",
        "readable",
        "ready",
        "processed",
        "analyzed",
        "analysis_complete",
    }

    successful_ocr = 0

    for doc in docs:
        ocr_status = (
            str(doc.ocr_status or "")
            .strip()
            .casefold()
        )

        if ocr_status in successful_ocr_statuses:
            successful_ocr += 1
            continue

        # Fallback to persisted OCR inspection metrics.
        # These values already exist in PostgreSQL and do not
        # trigger another OCR operation.
        readability = float(
            doc.readability_score or 0
        )

        confidence = float(
            doc.ocr_confidence or 0
        )

        sharpness = float(
            doc.sharpness_score or 0
        )

        if (
            readability > 0
            or confidence > 0
            or sharpness > 0
        ):
            successful_ocr += 1

    # ========================================================
    # 5. Documents with persisted quality issues
    # ========================================================

    quality_issue_documents = sum(
        1
        for doc in docs
        if bool(doc.quality_issues)
    )

    # ========================================================
    # 6. Readiness score
    #
    # Prefer the persisted readiness_score.
    #
    # For older records where readiness_score was not persisted
    # or is zero, derive a readiness estimate from the persisted
    # OCR inspection values. This does NOT invent OCR results and
    # does NOT re-run analysis.
    # ========================================================

    readiness_values = []

    for doc in docs:
        persisted_readiness = (
            float(doc.readiness_score)
            if doc.readiness_score is not None
            else 0.0
        )

        if persisted_readiness > 0:
            readiness_values.append(
                max(0.0, min(100.0, persisted_readiness))
            )
            continue

        readability = max(
            0.0,
            min(
                100.0,
                float(doc.readability_score or 0),
            ),
        )

        confidence = max(
            0.0,
            min(
                100.0,
                float(doc.ocr_confidence or 0) * 100,
            ),
        )

        sharpness = max(
            0.0,
            min(
                100.0,
                float(doc.sharpness_score or 0),
            ),
        )

        quality_issue_count = len(
            doc.quality_issues or []
        )

        # If the document has persisted OCR inspection data,
        # calculate a conservative readiness estimate.
        if (
            readability > 0
            or confidence > 0
            or sharpness > 0
        ):
            base_score = (
                readability * 0.40
                + confidence * 0.35
                + sharpness * 0.25
            )

            issue_penalty = min(
                quality_issue_count * 10.0,
                40.0,
            )

            derived_readiness = max(
                0.0,
                min(
                    100.0,
                    base_score - issue_penalty,
                ),
            )

            readiness_values.append(
                derived_readiness
            )

    average_readiness = (
        round(
            sum(readiness_values)
            / len(readiness_values),
            2,
        )
        if readiness_values
        else 0
    )

    # ========================================================
    # 7. Document type distribution
    # ========================================================

    type_counts: Dict[str, int] = {}

    for doc in docs:
        document_type = (
            doc.document_type
            or "General Document"
        )

        type_counts[document_type] = (
            type_counts.get(document_type, 0) + 1
        )

    # ========================================================
    # 8. Return frontend-compatible aggregate response
    # ========================================================

    return {
        "total_documents": total,

        # Frontend currently displays this value as
        # "Verified Documents". It represents documents whose
        # OCR/document-intelligence processing completed
        # successfully.
        "successful_ocr": successful_ocr,

        "quality_issues": quality_issue_documents,

        "pending_documents": pending,

        "verified_documents": verified,

        "rejected_documents": rejected,

        "average_readiness": average_readiness,

        "document_types": [
            {
                "type": document_type,
                "count": count,
            }
            for document_type, count
            in sorted(type_counts.items())
        ],
    }


# ============================================================
# GET INDIVIDUAL DOCUMENT DETAILS
# ============================================================

@router.get(
    "/{document_id}",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document details (Ownership enforced)",
)
def get_document_details(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    GET /api/v1/documents/{document_id}

    Retrieves document metadata and enforces ownership.
    """

    doc = crud_document.get_document_by_id(
        db,
        document_id,
    )

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Document with ID {document_id} "
                "not found."
            ),
        )

    if doc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Access denied: You do not own "
                "this document record."
            ),
        )

    return doc


# ============================================================
# RE-ANALYZE EXISTING DOCUMENT
# ============================================================

@router.post(
    "/{document_id}/analyze",
    response_model=DocumentAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Re-analyze an existing uploaded document",
)
def reanalyze_document(
    document_id: int,
    language: str = Query("en"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    POST /api/v1/documents/{document_id}/analyze

    Re-executes OCR and document intelligence for an existing
    document owned by the authenticated citizen.
    """

    doc = crud_document.get_document_by_id(
        db,
        document_id,
    )

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Document with ID {document_id} "
                "not found."
            ),
        )

    if doc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Access denied: You do not own "
                "this document record."
            ),
        )

    return document_service.analyze_document_file(
        db=db,
        user_id=current_user.id,
        file_path=doc.file_path,
        original_file_name=doc.file_name,
        mime_type=doc.mime_type,
        file_size_bytes=doc.file_size_bytes,
        language=language,
        application_id=doc.application_id,
        selected_document_type=doc.document_type,
    )


# ============================================================
# DELETE DOCUMENT
# ============================================================

@router.delete(
    "/{document_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Soft delete and physically remove document file (Ownership enforced)",
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    DELETE /api/v1/documents/{document_id}

    Removes the physical document file and soft-deletes
    the corresponding database record.

    Ownership is enforced.
    """

    doc = crud_document.get_document_by_id(
        db,
        document_id,
    )

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Document with ID {document_id} "
                "not found."
            ),
        )

    if doc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Access denied: You do not own "
                "this document record."
            ),
        )

    file_storage_util.delete_file(
        doc.file_path
    )

    crud_document.soft_delete_document(
        db,
        document_id,
    )

    return MessageResponse(
        message=(
            f"Document {document_id} "
            f"('{doc.file_name}') "
            "has been deleted successfully."
        )
    )