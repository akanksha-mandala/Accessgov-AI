import pytest
from document_intelligence.validators import document_validator
from document_intelligence.readiness_engine import document_readiness_engine
from document_intelligence.document_explainer import document_explainer


def test_missing_mandatory_fields_validation():
    """
    Test validation detects missing mandatory fields.
    """
    fields = {"name": "John Doe"}  # Missing mandatory 'aadhaar_number' and 'dob'
    val_res = document_validator.validate_extracted_fields("Aadhaar Card", fields)
    assert val_res.is_valid is False
    assert val_res.validation_status == "incomplete"
    assert "aadhaar_number" in val_res.missing_fields


def test_readiness_score_boundary_zero():
    """
    Test readiness score boundary 0.0 for Unknown Document.
    """
    val_res = document_validator.validate_extracted_fields("Unknown Document", {})
    readiness = document_readiness_engine.calculate_readiness(
        document_type="Unknown Document",
        extracted_fields={},
        validation_result=val_res,
        ocr_confidence=0.0
    )
    assert readiness.readiness_score == 0.0


def test_readiness_score_boundary_hundred():
    """
    Test readiness score boundary 100.0 for fully valid complete document.
    """
    fields = {"aadhaar_number": "XXXX-XXXX-9012", "dob": "01/01/1990", "gender": "Male"}
    val_res = document_validator.validate_extracted_fields("Aadhaar Card", fields, ocr_confidence=1.0)
    readiness = document_readiness_engine.calculate_readiness(
        document_type="Aadhaar Card",
        extracted_fields=fields,
        validation_result=val_res,
        ocr_confidence=1.0
    )
    assert readiness.readiness_score == 100.0


def test_explainer_disclaimer():
    """
    Test document explainer includes AI-assisted readiness check disclaimer.
    """
    val_res = document_validator.validate_extracted_fields("Income Certificate", {"annual_income": "₹1,50,000"})
    readiness = document_readiness_engine.calculate_readiness("Income Certificate", {"annual_income": "₹1,50,000"}, val_res, 0.90)
    exp = document_explainer.generate_explanation("Income Certificate", readiness, val_res)
    assert "AI-assisted document readiness check, not official" in exp
