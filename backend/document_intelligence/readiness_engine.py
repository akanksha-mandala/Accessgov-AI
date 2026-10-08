import logging
from typing import List, Dict, Any, Optional
from schemas.document import ReadinessResult, ValidationResult

logger = logging.getLogger("accessgov.document_intelligence.readiness_engine")


class DocumentReadinessEngine:
    """
    Deterministic Document Readiness Calculation Engine (Refinement #6).
    Evaluates completeness percentage (50%), OCR text confidence (30%), and field validity (20%).
    Outputs a score between 0.0 and 100.0.
    Explicitly clarifies that results are AI-assisted readiness checks and NOT official government certification.
    """

    @staticmethod
    def calculate_readiness(
        document_type: str,
        extracted_fields: Dict[str, Optional[str]],
        validation_result: ValidationResult,
        ocr_confidence: float
    ) -> ReadinessResult:
        """
        Calculates deterministic document readiness score and generates recommended next steps.
        """
        if document_type == "Unknown Document":
            return ReadinessResult(
                readiness_score=0.0,
                completeness_percentage=0.0,
                missing_fields=["All mandatory fields unverified"],
                low_confidence_fields=["Unrecognized document format"],
                next_steps=[
                    "Re-upload a clearer image or PDF of a supported government document (Aadhaar, PAN, Income Certificate, etc.)."
                ],
                evaluation_summary="Document type unrecognized. AI-assisted document readiness check, not official government certification."
            )

        total_fields = len(extracted_fields) if extracted_fields else 1
        populated_fields = sum(1 for v in extracted_fields.values() if v and v != "None" and str(v).strip() != "")
        
        completeness = (populated_fields / total_fields) * 100.0

        # 1. Component Weighting
        completeness_weight = (completeness / 100.0) * 50.0  # Max 50 points
        ocr_weight = (min(1.0, max(0.0, ocr_confidence))) * 30.0  # Max 30 points
        validity_weight = 20.0 if validation_result.is_valid else 5.0  # Max 20 points

        raw_score = completeness_weight + ocr_weight + validity_weight
        final_score = round(min(100.0, max(0.0, raw_score)), 1)

        low_confidence_fields = []
        if ocr_confidence < 0.70:
            low_confidence_fields.append("Overall OCR Text Quality")

        next_steps = []
        if validation_result.missing_fields:
            next_steps.append(f"Upload document version containing missing fields: {', '.join(validation_result.missing_fields)}.")
        if ocr_confidence < 0.70:
            next_steps.append("Re-upload a higher resolution, well-lit image to improve text readability.")
        if final_score >= 80.0:
            next_steps.append("Document quality is sufficient for scheme application attachment.")
        else:
            next_steps.append("Review extracted fields and upload a clearer copy to reach 100% readiness.")

        summary_text = (
            f"Document quality readiness check score: {final_score}/100. "
            f"AI-assisted document readiness check, not official government certification."
        )

        return ReadinessResult(
            readiness_score=final_score,
            completeness_percentage=round(completeness, 1),
            missing_fields=validation_result.missing_fields,
            low_confidence_fields=low_confidence_fields,
            next_steps=next_steps,
            evaluation_summary=summary_text
        )


document_readiness_engine = DocumentReadinessEngine()
