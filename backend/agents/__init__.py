"""Agent package exports.

Imports are intentionally lazy to avoid circular imports between the agent
package, translation service, and tool wrappers during FastAPI startup.
"""

_LAZY = {
    "ADKConfig": ("agents.adk_config", "ADKConfig"),
    "adk_config": ("agents.adk_config", "adk_config"),
    "SYSTEM_PROMPT": ("agents.prompts", "SYSTEM_PROMPT"),
    "ELIGIBILITY_PROMPT": ("agents.prompts", "ELIGIBILITY_PROMPT"),
    "DISCOVERY_PROMPT": ("agents.prompts", "DISCOVERY_PROMPT"),
    "GUIDANCE_PROMPT": ("agents.prompts", "GUIDANCE_PROMPT"),
    "SIMPLE_LANGUAGE_PROMPT": ("agents.prompts", "SIMPLE_LANGUAGE_PROMPT"),
    "SessionManager": ("agents.session_manager", "SessionManager"),
    "session_manager": ("agents.session_manager", "session_manager"),
    "IntentRouter": ("agents.intent_router", "IntentRouter"),
    "intent_router": ("agents.intent_router", "intent_router"),
    "ADKTools": ("agents.tools", "ADKTools"),
    "adk_tools": ("agents.tools", "adk_tools"),
    "ConversationAgent": ("agents.conversation_agent", "ConversationAgent"),
    "conversation_agent": ("agents.conversation_agent", "conversation_agent"),
}


def __getattr__(name):
    if name not in _LAZY:
        raise AttributeError(f"module 'agents' has no attribute {name!r}")
    import importlib
    module_name, attr_name = _LAZY[name]
    value = getattr(importlib.import_module(module_name), attr_name)
    globals()[name] = value
    return value


__all__ = list(_LAZY)
