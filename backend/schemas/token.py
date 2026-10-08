from typing import Optional
from pydantic import BaseModel


class TokenUser(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    phone_number: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None


class Token(BaseModel):
    """JWT response returned after login/registration/refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Optional[TokenUser] = None


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str
