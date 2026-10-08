from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
import enum
from database import Base


class ApplicationStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class Application(Base):
    """
    Application Model tracking government scheme applications submitted by users.
    Stores reference numbers, statuses, readiness scores, AI rejection notes, and step tracking.
    """
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    application_number = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("government_services.id", ondelete="RESTRICT"), nullable=False, index=True)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.SUBMITTED, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    district = Column(String(100), nullable=True, index=True)

    # Session 2 Model Updates
    readiness_score = Column(Float, default=0.0, nullable=False)
    rejection_reason_ai = Column(Text, nullable=True)
    completion_percentage = Column(Float, default=0.0, nullable=False)
    current_step = Column(String(100), default="initial", nullable=True)

    submitted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="applications")
    service = relationship("GovernmentService", back_populates="applications")
    uploaded_documents = relationship("UploadedDocument", back_populates="application")

    def __repr__(self):
        return f"<Application(id={self.id}, app_no='{self.application_number}', status='{self.status}')>"
