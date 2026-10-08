from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from models.users import User, UserRole
from security import decode_access_token
import crud.crud_user as crud_user
from config import settings

# OAuth2 Bearer token extractor
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    FastAPI Dependency: Decodes JWT Bearer token and returns authenticated User entity from database.
    Raises HTTP 401 Unauthorized if token is missing, invalid, or user does not exist.
    """
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: Missing subject claim.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = crud_user.get_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with this token does not exist.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    FastAPI Dependency: Verifies current authenticated user is active.
    Raises HTTP 403 Forbidden if user account is deactivated.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated."
        )
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    FastAPI Dependency: Restricts access exclusively to Admin users.
    Raises HTTP 403 Forbidden if user is not an Admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Admin role required."
        )
    return current_user


def get_current_official_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    FastAPI Dependency: Restricts access to Government Officials and Admins.
    Raises HTTP 403 Forbidden if user is a standard citizen.
    """
    if current_user.role not in [UserRole.OFFICIAL, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Government Official role required."
        )
    return current_user
