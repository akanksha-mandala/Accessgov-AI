from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel

DataT = TypeVar("DataT")


class MessageResponse(BaseModel):
    """
    Standard message response wrapper for simple status feedback.
    """
    message: str
    success: bool = True


class ResponseSchema(BaseModel, Generic[DataT]):
    """
    Generic API response schema for standardized envelope responses.
    """
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[DataT] = None


class PaginatedResponse(BaseModel, Generic[DataT]):
    """
    Paginated API response schema wrapping arrays of records.
    """
    total: int
    page: int
    size: int
    items: List[DataT]
