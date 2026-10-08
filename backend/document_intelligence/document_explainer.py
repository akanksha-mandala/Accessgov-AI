import logging
from typing import Dict, Any, Optional
from schemas.document import ReadinessResult, ValidationResult

logger = logging.getLogger("accessgov.document_intelligence.document_explainer")


class DocumentExplainer:
    """
    Citizen-Friendly Document Explainer (Refinement #7).
    Uses Module 3 simplifier and translation services to generate plain-language explanations of document analysis results.
    Explicitly includes mandatory legal disclaimers.
    """

    @staticmethod
    def generate_explanation(
        document_type: str,
        readiness_result: ReadinessResult,
        validation_result: ValidationResult,
        language: str = "en"
    ) -> str:
        """
        Generates structured plain-language explanation of document quality and missing items.
        """
        from services.simplifier import simplifier_service
        from services.translation_service import translation_service

        if document_type == "Unknown Document":
            explanation = (
                "The uploaded file could not be recognized as a standard government document. "
                "Please make sure the document is well-lit, fully visible, and not blurry."
            )
            return translation_service.translate_text(explanation, target_lang=language)

        # 1. Fetch Terminology Simplification
        simplification = simplifier_service.simplify_term(document_type, language=language)

        status_prefix = "High Quality" if readiness_result.readiness_score >= 80.0 else "Needs Improvement"
        
        lines = [
            f"Document Type: {document_type} (Status: {status_prefix})",
            f"Explanation: {simplification.simple_explanation}",
            f"Readiness Score: {readiness_result.readiness_score}/100",
        ]

        if validation_result.missing_fields:
            lines.append(f"Missing Details: {', '.join(validation_result.missing_fields)}")

        if readiness_result.next_steps:
            lines.append("Recommended Action:")
            for step in readiness_result.next_steps:
                lines.append(f"• {step}")

        lines.append("\nNote: AI-assisted document readiness check, not official government certification.")

        full_explanation = "\n".join(lines)
        return translation_service.translate_text(full_explanation, target_lang=language)


document_explainer = DocumentExplainer()
