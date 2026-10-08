from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict


class GovernmentServiceResponse(BaseModel):
    """
    Schema for government service catalog responses.
    """
    id: int
    title: str
    code: str
    category: str
    service_category: str
    department: str
    department_name: str
    description: str
    eligibility_criteria: Optional[str] = None
    required_documents_summary: Optional[str] = None
    processing_time_days: int
    processing_days: int
    fee_amount: str
    validity_period: str
    is_active: bool
    service_status: str
    available_online: bool
    state: str
    district_support: Optional[Any] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ServiceSearchRequest(BaseModel):
    """
    Schema for natural language and keyword search queries.
    """
    query: str
    category: Optional[str] = None
    department: Optional[str] = None
    district: Optional[str] = None
    limit: int = 10


class ServiceDiscoveryRequest(BaseModel):
    """
    Schema for citizen service discovery based on citizen profile or intent.
    """
    query: Optional[str] = None
    user_category: Optional[str] = None
    district: Optional[str] = None
    language: str = "en"


class ServiceCategoryResponse(BaseModel):
    """
    Schema listing service categories and counts.
    """
    category: str
    count: int
    departments: List[str]


class ServiceCreateRequest(BaseModel):
    """
    Schema for Admin creation of a new government service.
    """
    title: str
    code: str
    category: str
    department: str
    description: str
    eligibility_criteria: Optional[str] = None
    required_documents_summary: Optional[str] = None
    processing_days: int = 7
    fee_amount: str = "Free"
    validity_period: str = "1 Year"
    state: str = "Statewide"
    district_support: List[str] = ["All Districts"]


class ServiceUpdateRequest(BaseModel):
    """
    Schema for Admin updating an existing government service.
    """
    title: Optional[str] = None
    category: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    eligibility_criteria: Optional[str] = None
    required_documents_summary: Optional[str] = None
    processing_days: Optional[int] = None
    fee_amount: Optional[str] = None
    validity_period: Optional[str] = None
    service_status: Optional[str] = None
    available_online: Optional[bool] = None
