from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from models.users import UserRole


class UserBase(BaseModel):
    """
    Base user properties shared across request/response schemas.
    """
    full_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    district: Optional[str] = None
    preferred_language: str = "en"


class UserCreate(UserBase):
    """
    Schema for creating/registering a new user account.
    """
    password: str
    role: UserRole = UserRole.CITIZEN


class UserUpdate(BaseModel):
    """
    Schema for updating user profile information.
    """
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    district: Optional[str] = None
    preferred_language: Optional[str] = None
    profile_photo_url: Optional[str] = None


class UserPreferencesUpdate(BaseModel):
    """
    Schema for updating user accessibility and preference settings (PATCH /api/v1/users/preferences).
    """
    preferred_language: Optional[str] = None
    preferred_voice_enabled: Optional[bool] = None
    high_contrast_enabled: Optional[bool] = None
    font_scale: Optional[float] = None
    district: Optional[str] = None


class UserResponse(UserBase):
    """
    Schema for user profile responses returned by API endpoints.
    """
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    email_verified_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    profile_photo_url: Optional[str] = None
    preferred_voice_enabled: bool = False
    high_contrast_enabled: bool = False
    font_scale: float = 1.0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
