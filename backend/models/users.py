from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Float
from sqlalchemy.orm import relationship
import enum
from database import Base


class UserRole(str, enum.Enum):
    CITIZEN = "citizen"
    OFFICIAL = "official"
    ADMIN = "admin"


class User(Base):
    """
    User Model representing platform users (citizens, government officials, admins).
    Contains identity details, security credentials, district info, preferences, and accessibility settings.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CITIZEN, nullable=False)
    district = Column(String(100), index=True, nullable=True)
    preferred_language = Column(String(10), default="en", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Session 2 Model Updates
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    profile_photo_url = Column(String(500), nullable=True)
    preferred_voice_enabled = Column(Boolean, default=False, nullable=False)
    high_contrast_enabled = Column(Boolean, default=False, nullable=False)
    font_scale = Column(Float, default=1.0, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    uploaded_documents = relationship("UploadedDocument", back_populates="user", cascade="all, delete-orphan")
    conversation_logs = relationship("ConversationLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
