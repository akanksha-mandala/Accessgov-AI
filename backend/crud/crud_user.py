from datetime import datetime, timezone
from typing import Optional, Union, Dict, Any
from sqlalchemy.orm import Session
from models.users import User, UserRole
from schemas.user import UserCreate, UserUpdate, UserPreferencesUpdate
from security import get_password_hash, verify_password


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Retrieves a user by primary key ID.
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Retrieves a user by email address (case-insensitive lookup).
    """
    return db.query(User).filter(User.email.ilike(email.strip())).first()


def get_user_by_phone(db: Session, phone_number: str) -> Optional[User]:
    """
    Retrieves a user by phone number.
    """
    if not phone_number:
        return None
    return db.query(User).filter(User.phone_number == phone_number.strip()).first()


def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Creates a new user record with hashed password.
    """
    hashed_pwd = get_password_hash(user_in.password)
    db_user = User(
        full_name=user_in.full_name,
        email=user_in.email.lower().strip(),
        phone_number=user_in.phone_number.strip() if user_in.phone_number else None,
        hashed_password=hashed_pwd,
        role=user_in.role,
        district=user_in.district,
        preferred_language=user_in.preferred_language,
        is_active=True,
        is_verified=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, db_user: User, user_in: Union[UserUpdate, Dict[str, Any]]) -> User:
    """
    Updates existing user details.
    """
    update_data = user_in if isinstance(user_in, dict) else user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(db_user, field) and value is not None:
            setattr(db_user, field, value)
    
    db_user.updated_at = datetime.now(timezone.utc)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_preferences(db: Session, db_user: User, prefs_in: UserPreferencesUpdate) -> User:
    """
    Updates user accessibility and localization preferences.
    """
    update_data = prefs_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(db_user, field) and value is not None:
            setattr(db_user, field, value)

    db_user.updated_at = datetime.now(timezone.utc)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_last_active_language(db: Session, user_id: int, language: str) -> Optional[User]:
    """
    Session 4 Helper: Updates the user's preferred active language based on recent chat interactions.
    """
    user = get_user_by_id(db, user_id)
    if user and language:
        user.preferred_language = language.lower().strip()
        user.updated_at = datetime.now(timezone.utc)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticates a user by email and plain-text password.
    Returns User object if credentials are valid, None otherwise.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_last_login(db: Session, user_id: int) -> Optional[User]:
    """
    Updates the last_login timestamp for a user.
    """
    user = get_user_by_id(db, user_id)
    if user:
        user.last_login = datetime.now(timezone.utc)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def verify_user_email(db: Session, user_id: int) -> Optional[User]:
    """
    Marks a user's email as verified.
    """
    user = get_user_by_id(db, user_id)
    if user:
        user.is_verified = True
        user.email_verified_at = datetime.now(timezone.utc)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def set_user_password(db: Session, user_id: int, new_password: str) -> Optional[User]:
    """
    Resets a user's password with a new bcrypt hashed password.
    """
    user = get_user_by_id(db, user_id)
    if user:
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.now(timezone.utc)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
