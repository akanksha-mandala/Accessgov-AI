import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("accessgov.document_intelligence.field_extractors")


def mask_aadhaar(number: str) -> str:
    """
    Masks 12-digit Aadhaar number for PII privacy compliance (Refinement #1).
    Example: '1234 5678 9012' -> 'XXXX-XXXX-9012'.
    """
    digits = re.sub(r"\D", "", number)
    if len(digits) == 12:
        return f"XXXX-XXXX-{digits[-4:]}"
    return "XXXX-XXXX-XXXX"


def mask_pan(pan: str) -> str:
    """
    Masks 10-character PAN number for PII privacy compliance (Refinement #1).
    Example: 'ABCDE1234F' -> 'XXXXX1234F'.
    """
    clean = pan.strip().upper()
    if len(clean) == 10:
        return f"XXXXX{clean[5:]}"
    return "XXXXXXXXXX"


def mask_bank_account(account: str) -> str:
    """
    Masks Bank Account number for PII privacy compliance (Refinement #1).
    Example: '987654321012' -> 'XXXX-XXXX-1012'.
    """
    digits = re.sub(r"\D", "", account)
    if len(digits) >= 4:
        return f"XXXX-XXXX-{digits[-4:]}"
    return "XXXX-XXXX-XXXX"


class FieldExtractorEngine:
    """
    Regex & Pattern Field Extractor Engine (Refinement #5).
    Extracts structured fields per document type without LLM hallucinations.
    Missing fields remain missing (`None`). Enforces strict PII masking on sensitive identifiers.
    """

    @staticmethod
    def extract_fields(document_type: str, text: str) -> Dict[str, Optional[str]]:
        """
        Routes text to document-specific field extractor function based on classified document type.
        """
        if not text:
            return {}

        doc_type_lower = document_type.lower()
        if "aadhaar" in doc_type_lower:
            return FieldExtractorEngine.extract_aadhaar_fields(text)
        elif "pan" in doc_type_lower:
            return FieldExtractorEngine.extract_pan_fields(text)
        elif "income" in doc_type_lower:
            return FieldExtractorEngine.extract_income_certificate_fields(text)
        elif "caste" in doc_type_lower or "community" in doc_type_lower:
            return FieldExtractorEngine.extract_caste_certificate_fields(text)
        elif "domicile" in doc_type_lower or "residence" in doc_type_lower:
            return FieldExtractorEngine.extract_domicile_certificate_fields(text)
        elif "bank" in doc_type_lower or "passbook" in doc_type_lower:
            return FieldExtractorEngine.extract_bank_passbook_fields(text)

        return FieldExtractorEngine.extract_general_fields(text, document_type)

    @staticmethod
    def extract_aadhaar_fields(text: str) -> Dict[str, Optional[str]]:
        """
        Extracts Aadhaar fields: name, aadhaar_number, dob, gender.
        Masks aadhaar_number in output.
        """
        fields = {
            "name": None,
            "aadhaar_number": None,
            "dob": None,
            "gender": None
        }
        # Regex for Aadhaar 12-digit pattern
        match_aadhaar = re.search(r"\b(\d{4}\s?\d{4}\s?\d{4})\b", text)
        if match_aadhaar:
            raw_num = match_aadhaar.group(1)
            fields["aadhaar_number"] = mask_aadhaar(raw_num)

        # Regex for DOB / Year of Birth
        match_dob = re.search(r"(?:dob|date of birth|yob|birth year)[:\s]*(\d{2}/\d{2}/\d{4}|\d{4})", text, re.IGNORECASE)
        if match_dob:
            fields["dob"] = match_dob.group(1)

        # Regex for Gender
        match_gender = re.search(r"\b(male|female|transgender)\b", text, re.IGNORECASE)
        if match_gender:
            fields["gender"] = match_gender.group(1).capitalize()

        return fields

    @staticmethod
    def extract_pan_fields(text: str) -> Dict[str, Optional[str]]:
        """
        Extracts PAN fields: pan_number, name, father_name, dob.
        Masks pan_number in output.
        """
        fields = {
            "name": None,
            "pan_number": None,
            "father_name": None,
            "dob": None
        }
        # Regex for 10-char PAN format
        match_pan = re.search(r"\b([A-Z]{5}\d{4}[A-Z]{1})\b", text)
        if match_pan:
            raw_pan = match_pan.group(1)
            fields["pan_number"] = mask_pan(raw_pan)

        # Regex for DOB
        match_dob = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", text)
        if match_dob:
            fields["dob"] = match_dob.group(1)

        return fields

    @staticmethod
    def extract_income_certificate_fields(text: str) -> Dict[str, Optional[str]]:
        """
        Extracts Income Certificate fields: applicant_name, annual_income, issuing_authority, issue_date.
        """
        fields = {
            "applicant_name": None,
            "annual_income": None,
            "issuing_authority": None,
            "issue_date": None
        }
        # Regex for Annual Income amount
        match_income = re.search(r"(?:annual income|income is|rs\.?)\s*[:\s]*[₹rs\. ]*([\d,]+)", text, re.IGNORECASE)
        if match_income:
            income_str = match_income.group(1).replace(",", "")
            if income_str.isdigit():
                fields["annual_income"] = f"₹{int(income_str):,}"

        # Regex for Issue Date
        match_date = re.search(r"\b(\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})\b", text)
        if match_date:
            fields["issue_date"] = match_date.group(1)

        if "tahsildar" in text.lower():
            fields["issuing_authority"] = "Tahsildar / Revenue Department"

        return fields

    @staticmethod
    def extract_caste_certificate_fields(text: str) -> Dict[str, Optional[str]]:
        """
        Extracts Caste/Community fields: caste, category, certificate_number, district.
        """
        fields = {
            "caste": None,
            "category": None,
            "certificate_number": None,
            "district": None
        }
        # Category matching
        match_cat = re.search(r"\b(SC|ST|OBC|MBC|BC|EWS)\b", text, re.IGNORECASE)
        if match_cat:
            fields["category"] = match_cat.group(1).upper()

        match_cert_no = re.search(r"(?:certificate no|tn-)\s*[:\s]*([A-Z0-9/-]+)", text, re.IGNORECASE)
        if match_cert_no:
            fields["certificate_number"] = match_cert_no.group(1)

        return fields

    @staticmethod
    def extract_domicile_certificate_fields(text: str) -> Dict[str, Optional[str]]:
        """
        Extracts Domicile Certificate fields: resident_name, state, district, certificate_number.
        """
        fields = {
            "resident_name": None,
            "state": "Tamil Nadu",
            "district": None,
            "certificate_number": None
        }
        match_cert_no = re.search(r"(?:certificate no|ref no)\s*[:\s]*([A-Z0-9/-]+)", text, re.IGNORECASE)
        if match_cert_no:
            fields["certificate_number"] = match_cert_no.group(1)

        return fields

    @staticmethod
    def extract_bank_passbook_fields(text: str) -> Dict[str, Optional[str]]:
        """
        Extracts Bank Passbook fields: account_number, ifsc_code, bank_name.
        Masks account_number in output.
        """
        fields = {
            "account_number": None,
            "ifsc_code": None,
            "bank_name": None
        }
        # IFSC Code pattern: 4 letters, 0, 6 alphanumeric
        match_ifsc = re.search(r"\b([A-Z]{4}0[A-Z0-9]{6})\b", text)
        if match_ifsc:
            fields["ifsc_code"] = match_ifsc.group(1)

        # Bank Account Number pattern
        match_acc = re.search(r"(?:account|ac|a/c)\s*(?:no|number)?\s*[:\s]*(\d{9,18})", text, re.IGNORECASE)
        if match_acc:
            raw_acc = match_acc.group(1)
            fields["account_number"] = mask_bank_account(raw_acc)

        return fields

    @staticmethod
    def extract_general_fields(text: str, document_type: str) -> Dict[str, Optional[str]]:
        """
        General fallback field extractor.
        """
        fields = {
            "document_type": document_type,
            "issue_date": None,
            "reference_number": None
        }
        match_date = re.search(r"\b(\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})\b", text)
        if match_date:
            fields["issue_date"] = match_date.group(1)

        return fields


field_extractor_engine = FieldExtractorEngine()
