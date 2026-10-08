from typing import Optional
from pydantic import BaseModel, EmailStr
from models.users import UserRole


class RegisterRequest(BaseModel):
    """
    Schema for citizen registration requests.
    """
    full_name: str
    email: EmailStr
    password: str
    phone_number: Optional[str] = None
    district: Optional[str] = None
    preferred_language: str = "en"
    role: UserRole = UserRole.CITIZEN


class LoginRequest(BaseModel):
    """
    Schema for user authentication login requests.
    """
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    """
    Schema for initiating a password reset workflow.
    """
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """
    Schema for completing a password reset using a reset token.
    """
    token: str
    new_password: str


class VerifyEmailRequest(BaseModel):
    """
    Schema for verifying user email address using verification token.
    """
    token: str
