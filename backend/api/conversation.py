from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from database import get_db
from schemas.agent import ConversationRequest, ConversationResponse
from agents.conversation_agent import conversation_agent
from services.conversation_service import conversation_service
from security import decode_access_token
import crud.crud_user as crud_user

router = APIRouter(prefix="/conversation", tags=["Google ADK Conversation Agent"])


def get_optional_user_id(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[int]:
    """
    Optional Auth Helper: Extracts user_id from Bearer token if provided, without blocking guest citizens.
    """
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")
            if user_id:
                return int(user_id)
        except Exception:
            pass
    return None


@router.post(
    "/chat",
    response_model=ConversationResponse,
    status_code=status.HTTP_200_OK,
    summary="Interactive citizen chat with Google ADK Conversation Agent"
)
def chat_endpoint(
    request: ConversationRequest,
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_optional_user_id)
):
    """
    POST /api/v1/conversation/chat endpoint (Refinement #8).
    Processes citizen text message using the Google ADK Conversation Agent.
    Routes intents, invokes backend service tools, synthesizes response, logs interaction, and returns structured result.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty."
        )

    # 1. Update user's last active language if authenticated
    if user_id and request.language:
        crud_user.update_last_active_language(db, user_id, request.language)

    # 2. Process request through Conversation Agent Orchestrator
    response = conversation_agent.process_citizen_request(
        db=db,
        request=request,
        user_id=user_id
    )

    # 3. Log interaction to database asynchronously/synchronously
    service_code = response.suggested_service.get("code") if response.suggested_service else None
    conversation_service.log_interaction(
        db=db,
        session_id=response.conversation_session_id,
        user_id=user_id,
        user_message=request.message,
        assistant_response=response.response,
        language=request.language,
        intent=response.detected_intent,
        agent_used="Google ADK Conversation Agent",
        response_time_ms=response.response_time_ms,
        service_context=service_code
    )

    return response


@router.get(
    "/history/{session_id}",
    status_code=status.HTTP_200_OK,
    summary="Retrieve session chat history"
)
def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    GET /api/v1/conversation/history/{session_id} endpoint.
    Retrieves chronological chat log messages for a given session UUID.
    """
    history = conversation_service.get_conversation_history(db, session_id=session_id)
    return {
        "session_id": session_id,
        "total_messages": len(history),
        "history": history
    }
