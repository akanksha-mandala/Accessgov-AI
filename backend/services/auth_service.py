from datetime import timedelta, datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.users import User, UserRole
from schemas.auth import RegisterRequest, LoginRequest
from schemas.user import UserCreate
from schemas.token import Token
import crud.crud_user as crud_user
from security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    decode_token,
)
from services.email_service import email_service
from config import settings


class AuthService:
    """
    Authentication Business Logic Service.
    Coordinates registration, login, token refresh, password resets, and email verification.
    """

    @staticmethod
    def register_user(db: Session, register_in: RegisterRequest) -> User:
        """
        Registers a new user account (Citizen, Official, or Admin).
        Checks for duplicate email or phone before creation.
        """
        existing_email = crud_user.get_user_by_email(db, register_in.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists."
            )

        if register_in.phone_number:
            existing_phone = crud_user.get_user_by_phone(db, register_in.phone_number)
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A user with this phone number already exists."
                )

        user_create = UserCreate(
            full_name=register_in.full_name,
            email=register_in.email,
            password=register_in.password,
            phone_number=register_in.phone_number,
            district=register_in.district,
            preferred_language=register_in.preferred_language,
            role=register_in.role
        )
        user = crud_user.create_user(db, user_create)
        
        # Dispatch verification email placeholder
        verification_token = create_access_token(
            subject=user.id,
            expires_delta=timedelta(hours=24),
            extra_claims={"type": "email_verification"}
        )
        email_service.send_verification_email(user.email, verification_token)
        return user

    @staticmethod
    def authenticate_and_create_tokens(db: Session, login_in: LoginRequest) -> Token:
        """
        Authenticates user credentials and issues signed Access and Refresh JWT Tokens.
        Updates user's last_login timestamp.
        """
        user = crud_user.authenticate_user(db, login_in.email, login_in.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated. Please contact support."
            )

        # Update last login timestamp
        crud_user.update_last_login(db, user.id)

        # Create JWT Claims
        extra_claims = {
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
            "email": user.email
        }
        access_token = create_access_token(subject=user.id, extra_claims=extra_claims)
        refresh_token = create_refresh_token(subject=user.id, extra_claims=extra_claims)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value if hasattr(user.role, "value") else str(user.role),
                "phone_number": getattr(user, "phone_number", None),
                "state": getattr(user, "state", None),
                "district": getattr(user, "district", None),
            },
        )

    @staticmethod
    def refresh_access_token(db: Session, refresh_token_str: str) -> Token:
        """
        Validates a JWT Refresh Token and issues a fresh Access and Refresh Token pair.
        """
        payload = decode_refresh_token(refresh_token_str)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload."
            )

        user = crud_user.get_user_by_id(db, int(user_id))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User inactive or no longer exists."
            )

        extra_claims = {
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
            "email": user.email
        }
        new_access_token = create_access_token(subject=user.id, extra_claims=extra_claims)
        new_refresh_token = create_refresh_token(subject=user.id, extra_claims=extra_claims)

        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value if hasattr(user.role, "value") else str(user.role),
                "phone_number": getattr(user, "phone_number", None),
                "state": getattr(user, "state", None),
                "district": getattr(user, "district", None),
            },
        )

    @staticmethod
    def initiate_password_reset(db: Session, email: str) -> bool:
        """
        Generates a password reset token and emails it to the user.
        Always returns True to prevent user enumeration attacks.
        """
        user = crud_user.get_user_by_email(db, email)
        if user and user.is_active:
            reset_token = create_access_token(
                subject=user.id,
                expires_delta=timedelta(hours=1),
                extra_claims={"type": "password_reset"}
            )
            email_service.send_password_reset_email(user.email, reset_token)
        return True

    @staticmethod
    def confirm_password_reset(db: Session, token: str, new_password: str) -> bool:
        """
        Validates password reset token and sets the new bcrypt password.
        """
        payload = decode_token(token)
        if payload.get("type") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type for password reset."
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token payload."
            )

        user = crud_user.get_user_by_id(db, int(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        crud_user.set_user_password(db, user.id, new_password)
        return True


auth_service = AuthService()
