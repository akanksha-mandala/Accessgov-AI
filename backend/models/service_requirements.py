from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class ServiceRequirement(Base):
    """
    ServiceRequirement Model linking specific document/eligibility requirements to a government service.
    Session 3 Update: Adds accepted file types, file size constraints, and verification requirement flags.
    """
    __tablename__ = "service_requirements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    service_id = Column(Integer, ForeignKey("government_services.id", ondelete="CASCADE"), nullable=False, index=True)
    document_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_mandatory = Column(Boolean, default=True, nullable=False)
    accepted_formats = Column(String(100), default="pdf,jpg,png", nullable=False)
    accepted_file_types = Column(String(100), default="pdf,jpg,png", nullable=False)
    max_file_size_mb = Column(Integer, default=5, nullable=False)
    verification_required = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    service = relationship("GovernmentService", back_populates="requirements")

    def __repr__(self):
        return f"<ServiceRequirement(id={self.id}, service_id={self.service_id}, doc='{self.document_name}')>"
