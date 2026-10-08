from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base


class AccessibilityMetric(Base):
    """
    AccessibilityMetric Model measuring UI accessibility metrics (e.g., screen reader usage, font sizing, high-contrast toggles, voice commands).
    """
    __tablename__ = "accessibility_metrics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    metric_name = Column(String(100), index=True, nullable=False)
    metric_value = Column(Float, nullable=False)
    page_or_component = Column(String(150), index=True, nullable=False)
    device_type = Column(String(50), nullable=True)

    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<AccessibilityMetric(id={self.id}, name='{self.metric_name}', val={self.metric_value})>"
