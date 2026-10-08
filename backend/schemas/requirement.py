from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class RequiredDocument(BaseModel):
    """
    Schema representing document requirement for a government scheme.
    """
    id: Optional[int] = None
    service_id: int
    document_name: str
    description: Optional[str] = None
    is_mandatory: bool = True
    accepted_formats: str = "pdf,jpg,png"
    accepted_file_types: str = "pdf,jpg,png"
    max_file_size_mb: int = 5
    verification_required: bool = True

    model_config = ConfigDict(from_attributes=True)


class SimpleExplanationResponse(BaseModel):
    """
    Schema for citizen-friendly terminology simplification.
    """
    original_term: str
    simple_explanation: str
    key_points: List[str]
    why_it_matters: str
    language: str = "en"
