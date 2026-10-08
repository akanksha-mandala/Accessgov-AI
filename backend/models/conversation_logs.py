from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from database import Base


class MessageType(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class InteractionChannel(str, enum.Enum):
    WEB_CHAT = "web_chat"
    VOICE = "voice"
    WHATSAPP = "whatsapp"
    SMS = "sms"


class ConversationLog(Base):
    """
    ConversationLog Model storing AI chat & voice interaction histories with citizens.
    Captures multi-lingual queries, assistant responses, intent detection, agent routing, and latency metrics.
    """
    __tablename__ = "conversation_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(100), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    message_type = Column(Enum(MessageType), nullable=False)
    content = Column(Text, nullable=False)
    language = Column(String(10), default="en", nullable=False)
    channel = Column(Enum(InteractionChannel), default=InteractionChannel.WEB_CHAT, nullable=False)

    # Session 2 Model Updates
    intent = Column(String(100), nullable=True, index=True)
    agent_used = Column(String(100), nullable=True, index=True)
    response_time_ms = Column(Integer, nullable=True)
    service_context = Column(String(100), nullable=True, index=True)

    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="conversation_logs")

    def __repr__(self):
        return f"<ConversationLog(id={self.id}, session_id='{self.session_id}', type='{self.message_type}')>"
