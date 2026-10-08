import pytest
from schemas.eligibility import EligibilityCheckRequest
from services.eligibility_engine import eligibility_engine


def test_eligibility_engine_scholarship_eligible():
    """
    Unit test evaluating eligible student scholarship request.
    """
    req = EligibilityCheckRequest(
        service_code="GOV-SCH-007",
        annual_income=180000,
        is_student=True,
        uploaded_document_types=["Aadhaar Card", "Income Certificate", "Caste Certificate"]
    )
    result = eligibility_engine.evaluate_eligibility(db=None, request=req)
    assert result.eligible is True
    assert result.readiness_score > 50.0


def test_eligibility_engine_pension_disqualified():
    """
    Unit test evaluating disqualified pension request due to age requirement.
    """
    req = EligibilityCheckRequest(
        service_code="GOV-PEN-009",
        age=35,  # Requires age >= 60
        annual_income=50000
    )
    result = eligibility_engine.evaluate_eligibility(db=None, request=req)
    assert result.eligible is False
    assert result.eligibility_status == "Not Eligible"
    assert len(result.disqualification_reasons) > 0
