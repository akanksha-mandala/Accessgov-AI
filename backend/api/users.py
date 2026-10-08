from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from models.users import User
from schemas.user import UserResponse, UserUpdate, UserPreferencesUpdate
from auth.dependencies import get_current_active_user
import crud.crud_user as crud_user

router = APIRouter(prefix="/users", tags=["Users & Preferences"])


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get authenticated user profile"
)
def get_user_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Authenticated User Profile endpoint.
    Returns details of the currently logged-in citizen/official/admin.
    """
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile"
)
def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update profile details for the authenticated user.
    """
    updated_user = crud_user.update_user(db, current_user, user_in)
    return updated_user


@router.patch(
    "/preferences",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user accessibility and localization preferences"
)
def update_preferences(
    prefs_in: UserPreferencesUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    PATCH /api/v1/users/preferences endpoint.
    Updates citizen accessibility settings (voice guidance, high-contrast, font scaling, preferred language, district).
    """
    updated_user = crud_user.update_user_preferences(db, current_user, prefs_in)
    return updated_user
