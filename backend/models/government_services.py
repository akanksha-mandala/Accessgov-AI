from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from database import Base


class GovernmentService(Base):
    """
    GovernmentService Model representing accessible public services scheme catalog.
    Session 3 Update: Includes comprehensive service metadata for intelligence engine, multi-district support, and soft status toggles.
    """
    __tablename__ = "government_services"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Category & Department details
    category = Column(String(100), nullable=False, index=True)
    service_category = Column(String(100), nullable=False, index=True)  # Alias / Detailed classification
    department = Column(String(255), nullable=False, index=True)
    department_name = Column(String(255), nullable=False, index=True)  # Official department name
    
    # Description & Criteria
    description = Column(Text, nullable=False)
    eligibility_criteria = Column(Text, nullable=True)
    required_documents_summary = Column(Text, nullable=True)
    
    # Service operational metrics
    processing_time_days = Column(Integer, default=7, nullable=False)
    processing_days = Column(Integer, default=7, nullable=False)  # Unified processing timeline
    fee_amount = Column(String(50), default="Free", nullable=False)
    validity_period = Column(String(100), default="1 Year", nullable=False)
    
    # Status & Accessibility
    is_active = Column(Boolean, default=True, nullable=False)
    service_status = Column(String(50), default="active", nullable=False, index=True)  # "active", "inactive", "maintenance"
    available_online = Column(Boolean, default=True, nullable=False)
    state = Column(String(100), default="Statewide", nullable=False)
    district_support = Column(JSON, default=list, nullable=True)  # List of districts where available, e.g. ["All", "Chennai", "Coimbatore"]

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    requirements = relationship("ServiceRequirement", back_populates="service", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="service", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<GovernmentService(id={self.id}, code='{self.code}', title='{self.title}', status='{self.service_status}')>"
