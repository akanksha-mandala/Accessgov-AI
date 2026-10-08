from typing import Optional, List
from pydantic import BaseModel, Field


class EligibilityCheckRequest(BaseModel):
    """
    Input schema for AccessGov AI eligibility evaluation.

    Supports both:
    - backend-native field names
    - frontend-friendly aliases used by the Eligibility Checker UI
    """

    service_id: Optional[int] = None
    service_code: Optional[str] = None

    age: Optional[int] = Field(
        default=None,
        description="Age of citizen in years"
    )

    gender: Optional[str] = Field(
        default=None,
        description="Male, Female, Other"
    )

    annual_income: Optional[float] = Field(
        default=None,
        description="Annual family/parental income in INR"
    )

    caste_category: Optional[str] = Field(
        default=None,
        description="General, SC, ST, OBC, BC, MBC, DNC, EWS"
    )

    disability_percentage: Optional[float] = Field(
        default=0.0,
        description="Percentage of disability"
    )

    is_disabled: Optional[bool] = Field(
        default=False,
        description="Disability status"
    )

    occupation: Optional[str] = Field(
        default=None,
        description="Student, Unemployed, Farmer, Self-Employed, etc."
    )

    is_student: Optional[bool] = Field(
        default=False,
        description="Student enrollment status"
    )

    district: Optional[str] = Field(
        default=None,
        description="District of residence"
    )

    state: Optional[str] = Field(
        default="Tamil Nadu",
        description="State of residence"
    )

    marital_status: Optional[str] = Field(
        default=None,
        description="Single, Married, Widowed"
    )

    # Frontend eligibility checker fields
    marks: Optional[float] = Field(
        default=None,
        description="Academic percentage"
    )

    has_land: Optional[bool] = Field(
        default=False,
        description="Whether applicant has land holdings"
    )

    uploaded_document_types: List[str] = Field(
        default_factory=list,
        description="List of uploaded document types"
    )


class EligibilityResult(BaseModel):
    """
    Structured output returned by the deterministic eligibility engine.
    """

    eligible: bool
    eligibility_status: str
    eligibility_score: float
    readiness_score: float

    required_documents: List[str]
    missing_documents: List[str]
    missing_conditions: List[str]
    next_steps: List[str]

    estimated_processing_days: int

    matched_rules: List[str] = Field(default_factory=list)
    disqualification_reasons: List[str] = Field(default_factory=list)