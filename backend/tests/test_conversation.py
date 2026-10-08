import pytest
from agents.intent_router import intent_router
from agents.session_manager import session_manager
from agents.tools import adk_tools
from agents.conversation_agent import conversation_agent
from schemas.agent import ConversationRequest
from schemas.eligibility import EligibilityCheckRequest


def test_intent_router_keyword_classification():
    """
    Unit test for Stage 1 rule/keyword-based intent classification.
    """
    pred_disc = intent_router.classify_intent("I need an income certificate")
    assert pred_disc.intent == "service_discovery"
    assert pred_disc.confidence >= 0.70

    pred_elig = intent_router.classify_intent("Am I eligible for a scholarship if my annual income is ₹2 lakh?")
    assert pred_elig.intent == "eligibility_check"
    assert pred_elig.confidence >= 0.70

    pred_greet = intent_router.classify_intent("Hello")
    assert pred_greet.intent == "greeting"
    assert pred_greet.confidence >= 0.90


def test_session_manager_memory_window():
    """
    Unit test for session memory window management.
    """
    session = session_manager.get_or_create_session(session_id="test_session_123")
    assert session.session_id == "test_session_123"

    session_manager.add_message("test_session_123", "user", "I need income certificate")
    session_manager.add_message("test_session_123", "assistant", "Sure, here are details.")

    formatted = session_manager.get_formatted_history("test_session_123")
    assert "Citizen: I need income certificate" in formatted
    assert "Assistant: Sure, here are details." in formatted


def test_adk_tools_execution():
    """
    Unit test for ADK Tool Wrappers invoking backend logic.
    """
    req = EligibilityCheckRequest(annual_income=150000, is_student=True)
    res = adk_tools.eligibility_tool(db=None, request=req)
    assert res.success is True
    assert res.tool_name == "eligibility_tool"
    assert res.data["eligible"] is True

    sim_res = adk_tools.simplifier_tool("Domicile Certificate")
    assert sim_res.success is True
    assert "permanently live" in sim_res.data["simple_explanation"].lower()


def test_conversation_agent_processing():
    """
    Unit test for full Conversation Agent orchestration flow.
    """
    req = ConversationRequest(
        message="I need an income certificate",
        language="en"
    )
    resp = conversation_agent.process_citizen_request(db=None, request=req)
    assert resp.conversation_session_id is not None
    assert resp.detected_intent in ["service_discovery", "greeting", "unknown"]
    assert len(resp.response) > 0
