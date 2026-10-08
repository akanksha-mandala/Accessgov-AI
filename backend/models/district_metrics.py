from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base


class DistrictMetric(Base):
    """
    DistrictMetric Model aggregating regional performance indicators, submission counts, approval rates, and digital adoption by district.
    """
    __tablename__ = "district_metrics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    district_name = Column(String(100), index=True, nullable=False)
    metric_type = Column(String(100), index=True, nullable=False)
    value = Column(Float, nullable=False)

    recorded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<DistrictMetric(id={self.id}, district='{self.district_name}', metric='{self.metric_type}', value={self.value})>"
