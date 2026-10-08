from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AgentMessage(BaseModel):
    """
    Represents a single chat message in the conversation session history.
    """
    role: str = Field(description="Message role: 'user', 'assistant', or 'system'")
    content: str = Field(description="Text message content")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConversationRequest(BaseModel):
    """
    Input schema for citizen chat interaction with the Conversation Agent.
    """
    message: str = Field(description="Citizen input query or text message")
    language: str = Field(default="en", description="Preferred response language (en, ta, te, hi, kn)")
    session_id: Optional[str] = Field(default=None, description="Optional existing conversation session UUID")
    district: Optional[str] = Field(default=None, description="Citizen district location context")
    page_context: Optional[str] = Field(default=None, description="Current frontend route/page context for accessibility-aware guidance")


class ConversationResponse(BaseModel):
    """
    Output schema returned by the Conversation API (Refinement #8).
    """
    response: str = Field(description="Synthesized conversational agent response")
    detected_intent: str = Field(description="Classified user intent")
    confidence: float = Field(description="Intent classification confidence score (0.0 to 1.0)")
    conversation_session_id: str = Field(description="Unique conversation session identifier")
    suggested_service: Optional[Dict[str, Any]] = Field(default=None, description="Matched government scheme metadata")
    sources_used: Optional[List[Dict[str, Any]]] = Field(default=None, description="RAG retrieved knowledge source metadata")
    response_time_ms: Optional[int] = Field(default=None, description="Processing latency in milliseconds")


class ConversationContext(BaseModel):
    """
    Internal session context state passed across agent tools and memory.
    """
    session_id: str
    user_id: Optional[int] = None
    history: List[AgentMessage] = []
    district: Optional[str] = None
    language: str = "en"


class IntentPrediction(BaseModel):
    """
    Structured output returned by the two-stage Intent Router.
    """
    intent: str
    confidence: float
    method: str  # "keyword_rules" or "llm_fallback"


class ToolExecutionResult(BaseModel):
    """
    Standardized JSON execution result returned by ADK tool wrappers (Refinement #4).
    """
    tool_name: str
    success: bool
    data: Any
    sources: Optional[List[Dict[str, Any]]] = None
    confidence: float = 1.0
    execution_message: Optional[str] = None
