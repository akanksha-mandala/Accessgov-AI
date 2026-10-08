from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, ConfigDict

from models.uploaded_documents import VerificationStatus


class OCRResult(BaseModel):
    """
    Schema for raw OCR processing results.
    """

    status: str = Field(
        description="'success' or 'ocr_failed'"
    )

    raw_text: str = Field(
        default="",
        description="Extracted document raw text"
    )

    confidence: float = Field(
        default=0.0,
        description="Overall OCR text extraction confidence score"
    )

    page_count: int = Field(
        default=1,
        description="Number of document pages parsed"
    )

    bounding_boxes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Extracted text region bounding boxes"
    )

    error_message: Optional[str] = Field(
        default=None,
        description="Detailed error message if OCR fails"
    )

    readability_score: float = Field(
        default=0.0,
        description="Physical document readability/quality score from 0 to 100"
    )

    quality_issues: List[str] = Field(
        default_factory=list,
        description="Detected physical document quality issues"
    )

    sharpness_score: float = Field(
        default=0.0,
        description="Image sharpness score from 0 to 100"
    )


class ExtractedField(BaseModel):
    """
    Schema representing a single extracted field
    (e.g. Aadhaar number, Income amount).
    """

    field_name: str
    value: Optional[str] = None
    masked_value: Optional[str] = None
    is_sensitive: bool = False
    confidence: float = 1.0
    is_valid: bool = True


class ValidationResult(BaseModel):
    """
    Schema for document field validation report.
    """

    is_valid: bool

    validation_status: str

    missing_fields: List[str] = Field(
        default_factory=list
    )

    warnings: List[str] = Field(
        default_factory=list
    )

    extracted_fields: Dict[str, Optional[str]] = Field(
        default_factory=dict
    )


class ReadinessResult(BaseModel):
    """
    Schema for document readiness check calculation.
    """

    readiness_score: float = Field(
        description="Deterministic score between 0.0 and 100.0"
    )

    completeness_percentage: float = Field(
        description="Percentage of mandatory fields populated"
    )

    missing_fields: List[str] = Field(
        default_factory=list
    )

    low_confidence_fields: List[str] = Field(
        default_factory=list
    )

    next_steps: List[str] = Field(
        default_factory=list
    )

    evaluation_summary: str = Field(
        default=(
            "AI-assisted document readiness check, "
            "not official government certification."
        )
    )


class DocumentUploadResponse(BaseModel):
    """
    Schema returned by the Personal Vault document listing endpoint.

    Includes both persisted document metadata and the latest
    automated OCR/quality inspection metrics.
    """

    id: int

    document_type: str

    file_name: str

    mime_type: str

    file_size_bytes: int

    verification_status: VerificationStatus

    uploaded_at: datetime

    # Automated inspection metadata
    readiness_score: Optional[float] = None

    readability_score: Optional[float] = None

    ocr_confidence: Optional[float] = None

    sharpness_score: Optional[float] = None

    quality_issues: List[str] = Field(
        default_factory=list
    )

    ocr_status: Optional[str] = None

    extracted_fields: Optional[Dict[str, Optional[str]]] = None

    validation_errors: Optional[List[str]] = None

    model_config = ConfigDict(
        from_attributes=True
    )


class DocumentAnalysisResponse(BaseModel):
    """
    Comprehensive schema returned by document intelligence
    analysis endpoints.
    """

    document_id: Optional[int] = None

    file_name: str

    document_type: str

    classification_confidence: float

    ocr_result: OCRResult

    extracted_fields: Dict[str, Optional[str]]

    validation_result: ValidationResult

    readiness_result: ReadinessResult

    explanation: str

    disclaimer: str = (
        "AI-assisted document readiness check, "
        "not official government certification."
    )
