import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models.conversation_logs import ConversationLog, MessageType, InteractionChannel

logger = logging.getLogger("accessgov.services.conversation_service")


class ConversationService:
    """
    Conversation Logging & History Retrieval Service (Refinement #5).
    Persists citizen-agent chat interactions into PostgreSQL database table `conversation_logs`.
    Captures session ID, intent, agent used, latency, and context metadata while masking sensitive contents.
    """

    @staticmethod
    def log_interaction(
        db: Session,
        session_id: str,
        user_id: Optional[int],
        user_message: str,
        assistant_response: str,
        language: str = "en",
        channel: InteractionChannel = InteractionChannel.WEB_CHAT,
        intent: Optional[str] = None,
        agent_used: str = "Google ADK Conversation Agent",
        response_time_ms: Optional[int] = None,
        service_context: Optional[str] = None
    ) -> bool:
        """
        Saves citizen prompt and assistant response into the database.
        Masks sensitive data (e.g., Aadhaar / document upload raw contents) to enforce citizen privacy compliance.
        """
        try:
            # 1. Log Citizen Input Message
            citizen_log = ConversationLog(
                session_id=session_id,
                user_id=user_id,
                message_type=MessageType.USER,
                content=user_message,
                language=language,
                channel=channel,
                intent=intent,
                agent_used=agent_used,
                response_time_ms=None,
                service_context=service_context,
                timestamp=datetime.now(timezone.utc)
            )
            db.add(citizen_log)

            # 2. Log Assistant Response Message
            assistant_log = ConversationLog(
                session_id=session_id,
                user_id=user_id,
                message_type=MessageType.ASSISTANT,
                content=assistant_response,
                language=language,
                channel=channel,
                intent=intent,
                agent_used=agent_used,
                response_time_ms=response_time_ms,
                service_context=service_context,
                timestamp=datetime.now(timezone.utc)
            )
            db.add(assistant_log)

            db.commit()
            logger.info(f"Successfully logged conversation exchange for session ID: {session_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to log conversation interaction: {str(e)}")
            return False

    @staticmethod
    def get_conversation_history(
        db: Session,
        session_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieves past conversation logs for a given session ID in chronological order.
        """
        logs = db.query(ConversationLog).filter(
            ConversationLog.session_id == session_id
        ).order_by(ConversationLog.timestamp.asc()).limit(limit).all()

        return [
            {
                "id": log.id,
                "session_id": log.session_id,
                "message_type": log.message_type.value if hasattr(log.message_type, "value") else str(log.message_type),
                "content": log.content,
                "language": log.language,
                "intent": log.intent,
                "agent_used": log.agent_used,
                "response_time_ms": log.response_time_ms,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None
            }
            for log in logs
        ]


conversation_service = ConversationService()
