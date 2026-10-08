import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from config import settings
from schemas.agent import AgentMessage, ConversationContext

logger = logging.getLogger("accessgov.agents.session_manager")


class SessionManager:
    """
    Session & Conversation Memory Manager (Refinement #3).
    Maintains chronological memory windows per session ID independently from Gemini LLM state.
    """

    def __init__(self, window_size: int = None):
        self.window_size = window_size or settings.AGENT_MEMORY_WINDOW
        # In-memory storage mapping session_id -> ConversationContext
        self._sessions: Dict[str, ConversationContext] = {}

    def get_or_create_session(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
        district: Optional[str] = None,
        language: str = "en"
    ) -> ConversationContext:
        """
        Retrieves an existing conversation session context or creates a new one with UUID.
        """
        if not session_id or session_id not in self._sessions:
            new_id = session_id or str(uuid.uuid4())
            ctx = ConversationContext(
                session_id=new_id,
                user_id=user_id,
                history=[],
                district=district,
                language=language
            )
            self._sessions[new_id] = ctx
            logger.info(f"Created new conversation session ID: {new_id}")
            return ctx

        ctx = self._sessions[session_id]
        if district:
            ctx.district = district
        if language:
            ctx.language = language
        return ctx

    def add_message(self, session_id: str, role: str, content: str) -> AgentMessage:
        """
        Appends a message to session history and trims context to the configured memory window.
        """
        ctx = self.get_or_create_session(session_id)
        msg = AgentMessage(
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc)
        )
        ctx.history.append(msg)

        # Enforce memory window limit
        if len(ctx.history) > self.window_size * 2:  # 2 messages per exchange (user + assistant)
            ctx.history = ctx.history[-(self.window_size * 2):]

        return msg

    def get_formatted_history(self, session_id: str) -> str:
        """
        Formats recent conversation history as plain text for prompt context.
        """
        ctx = self.get_or_create_session(session_id)
        if not ctx.history:
            return "No previous conversation context."

        lines = []
        for msg in ctx.history:
            role_label = "Citizen" if msg.role == "user" else "Assistant"
            lines.append(f"{role_label}: {msg.content}")
        return "\n".join(lines)


session_manager = SessionManager()
