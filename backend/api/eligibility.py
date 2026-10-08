from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.eligibility import EligibilityCheckRequest, EligibilityResult
from services.eligibility_engine import eligibility_engine

router = APIRouter(prefix="/services", tags=["Eligibility Engine"])


@router.post(
    "/eligibility-check",
    response_model=EligibilityResult,
    status_code=status.HTTP_200_OK,
    summary="Evaluate citizen eligibility for government schemes"
)
def check_eligibility(
    request: EligibilityCheckRequest,
    db: Session = Depends(get_db)
):
    """
    POST /api/v1/services/eligibility-check endpoint.
    Evaluates citizen demographics, income, caste, disability, occupation, and uploaded documents.
    Returns structured results including eligibility status, scores, readiness, missing conditions, and next steps (Refinement #4).
    """
    return eligibility_engine.evaluate_eligibility(db, request)
