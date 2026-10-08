from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, JSON, DateTime
from database import Base


class AnalyticsEvent(Base):
    """
    AnalyticsEvent Model capturing detailed system telemetry, search queries, scheme views, and interactions.
    Session 2 Update: Relies on anonymous user_hash instead of explicit user_id for strict citizen privacy compliance.
    """
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_hash = Column(String(64), index=True, nullable=True)  # Anonymous hashed user identifier for privacy
    event_type = Column(String(100), index=True, nullable=False)
    district = Column(String(100), index=True, nullable=True)
    payload = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<AnalyticsEvent(id={self.id}, event_type='{self.event_type}', user_hash='{self.user_hash}')>"
