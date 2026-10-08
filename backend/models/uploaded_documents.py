from datetime import datetime, timezone
import enum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Float, JSON
from sqlalchemy.orm import relationship

from database import Base


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class UploadedDocument(Base):
    """
    UploadedDocument Model tracking citizen uploaded documents,
    storage paths, MIME types, verification status, and persisted
    document intelligence inspection results.
    """
    __tablename__ = "uploaded_documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    application_id = Column(
        Integer,
        ForeignKey("applications.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    document_type = Column(
        String(100),
        nullable=False,
    )

    file_name = Column(
        String(255),
        nullable=False,
    )

    file_path = Column(
        String(500),
        nullable=False,
    )

    mime_type = Column(
        String(100),
        nullable=False,
    )

    file_size_bytes = Column(
        Integer,
        nullable=False,
    )

    verification_status = Column(
        Enum(VerificationStatus),
        default=VerificationStatus.PENDING,
        nullable=False,
    )

    rejection_reason = Column(
        String(255),
        nullable=True,
    )

    # ============================================================
    # Persisted Document Intelligence Results
    # ============================================================

    ocr_status = Column(
        String(50),
        nullable=True,
    )

    ocr_confidence = Column(
        Float,
        nullable=True,
    )

    readability_score = Column(
        Float,
        nullable=True,
    )

    sharpness_score = Column(
        Float,
        nullable=True,
    )

    readiness_score = Column(
        Float,
        nullable=True,
    )

    quality_issues = Column(
        JSON,
        nullable=True,
    )

    extracted_fields = Column(
        JSON,
        nullable=True,
    )

    validation_errors = Column(
        JSON,
        nullable=True,
    )

    uploaded_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ============================================================
    # Relationships
    # ============================================================

    user = relationship(
        "User",
        back_populates="uploaded_documents",
    )

    application = relationship(
        "Application",
        back_populates="uploaded_documents",
    )

    def __repr__(self):
        return (
            f"<UploadedDocument("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"file_name='{self.file_name}'"
            f")>"
        )