from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base


class Language(Base):
    """
    Language Model cataloging platform-supported regional languages, localization preferences, font scripts, and text direction.
    """
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(10), unique=True, index=True, nullable=False)  # ISO 639-1 code e.g. "en", "hi", "ta", "ur"
    name = Column(String(100), nullable=False)  # e.g. "English", "Hindi", "Tamil", "Urdu"
    native_name = Column(String(100), nullable=True)  # e.g. "हिन्दी", "தமிழ்", "اردو"
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)

    # Session 2 Model Updates
    is_rtl = Column(Boolean, default=False, nullable=False)  # Right-to-left layout direction flag
    language_family = Column(String(100), nullable=True)  # e.g. "Indo-Aryan", "Dravidian"

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<Language(id={self.id}, code='{self.code}', name='{self.name}', rtl={self.is_rtl})>"
