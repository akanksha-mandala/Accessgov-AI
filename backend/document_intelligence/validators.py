import re
import logging
from typing import Dict, Any, List, Optional
from schemas.document import ValidationResult

logger = logging.getLogger("accessgov.document_intelligence.validators")

MANDATORY_FIELDS_MAP = {
    "Aadhaar Card": ["aadhaar_number", "dob"],
    "PAN Card": ["pan_number"],
    "Income Certificate": ["annual_income"],
    "Community / Caste Certificate": ["category"],
    "Domicile Certificate": ["certificate_number"],
    "Bank Passbook": ["account_number", "ifsc_code"],
}


class DocumentValidator:
    """
    Document Field Validator (Refinements #5 & #6).
    Checks field presence, regex pattern validity, and missing mandatory values.
    Does NOT declare legal verification; performs document quality & readiness checks.
    """

    @staticmethod
    def validate_extracted_fields(
        document_type: str,
        fields: Dict[str, Optional[str]],
        ocr_confidence: float = 1.0
    ) -> ValidationResult:
        """
        Validates extracted fields for a given document type.
        """
        mandatory = MANDATORY_FIELDS_MAP.get(document_type, [])
        missing_fields = []
        warnings = []

        # 1. Check Missing Mandatory Fields
        for req_field in mandatory:
            val = fields.get(req_field)
            if not val or val == "None" or val.strip() == "":
                missing_fields.append(req_field)

        # 2. Pattern Format Warnings
        if document_type == "PAN Card" and "pan_number" in fields and fields["pan_number"]:
            val = fields["pan_number"]
            # Check if masked format matches XXXXX1234X or valid PAN format
            if not re.search(r"^[A-Z0-9]{10}$", val) and not val.startswith("XXXXX"):
                warnings.append("PAN number format check warning: Pattern does not match standard 10-char PAN.")

        if ocr_confidence < 0.70:
            warnings.append("Low OCR text extraction confidence. Please verify image clarity.")

        # 3. Determine Overall Validation Status
        if missing_fields:
            is_valid = False
            validation_status = "incomplete"
        elif warnings:
            is_valid = True
            validation_status = "valid_with_warnings"
        else:
            is_valid = True
            validation_status = "valid"

        return ValidationResult(
            is_valid=is_valid,
            validation_status=validation_status,
            missing_fields=missing_fields,
            warnings=warnings,
            extracted_fields=fields
        )


document_validator = DocumentValidator()
