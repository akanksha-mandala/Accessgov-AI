from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.auth import RegisterRequest, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest, VerifyEmailRequest
from schemas.token import Token, RefreshTokenRequest
from schemas.common import MessageResponse
from schemas.user import UserCreate
from models.users import UserRole
from services.auth_service import auth_service
import crud.crud_user as crud_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED, summary="Register a new citizen account")
def register_user(register_in: RegisterRequest, db: Session = Depends(get_db)):
    # Public registration is always a citizen registration.
    register_in.role = register_in.role.__class__.CITIZEN
    user = auth_service.register_user(db, register_in)
    return auth_service.authenticate_and_create_tokens(
        db, LoginRequest(email=user.email, password=register_in.password)
    )

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK, summary="User login (Citizen / Official / Admin)")
def login_user(login_in: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.authenticate_and_create_tokens(db, login_in)
@router.post("/demo-login", response_model=Token, status_code=status.HTTP_200_OK, summary="Demo login for citizen or admin")
def demo_login(role: str = Body("citizen", embed=True), db: Session = Depends(get_db)):
    if role not in {"citizen", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Demo role must be either citizen or admin."
        )

    if role == "admin":
        email = "demo.admin@accessgov.ai"
        password = "Admin@123"
        full_name = "AccessGov Demo Admin"
        user_role = UserRole.ADMIN
    else:
        email = "demo.citizen@accessgov.ai"
        password = "Citizen@123"
        full_name = "AccessGov Demo Citizen"
        user_role = UserRole.CITIZEN

    user = crud_user.get_user_by_email(db, email)

    if not user:
        user = crud_user.create_user(
            db,
            UserCreate(
                full_name=full_name,
                email=email,
                password=password,
                role=user_role,
                district="Virudhunagar",
                preferred_language="en",
            )
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo account is inactive."
        )

    return auth_service.authenticate_and_create_tokens(
        db,
        LoginRequest(email=email, password=password)
    )

@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK, summary="Refresh access token using valid refresh token")
def refresh_token(refresh_in: RefreshTokenRequest, db: Session = Depends(get_db)):
    return auth_service.refresh_access_token(db, refresh_in.refresh_token)

@router.post("/forgot-password", response_model=MessageResponse, status_code=status.HTTP_200_OK, summary="Initiate password reset workflow")
def forgot_password(forgot_in: ForgotPasswordRequest, db: Session = Depends(get_db)):
    auth_service.initiate_password_reset(db, forgot_in.email)
    return MessageResponse(message="If a user with this email exists, a password reset link has been dispatched.")

@router.post("/reset-password", response_model=MessageResponse, status_code=status.HTTP_200_OK, summary="Reset password using reset token")
def reset_password(reset_in: ResetPasswordRequest, db: Session = Depends(get_db)):
    auth_service.confirm_password_reset(db, reset_in.token, reset_in.new_password)
    return MessageResponse(message="Password has been successfully updated. You may now log in with your new password.")

@router.post("/verify-email", response_model=MessageResponse, status_code=status.HTTP_200_OK, summary="Verify citizen email address")
def verify_email(verify_in: VerifyEmailRequest, db: Session = Depends(get_db)):
    from security import decode_token
    payload = decode_token(verify_in.token)
    if payload.get("type") != "email_verification":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token type for email verification.")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token payload.")
    user = crud_user.verify_user_email(db, int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return MessageResponse(message="Email address successfully verified.")
