from api.auth import router as auth_router
from api.users import router as users_router
from api.services import router as services_router
from api.eligibility import router as eligibility_router
from api.discovery import router as discovery_router
from api.conversation import router as conversation_router
from api.documents import router as documents_router

__all__ = [
    "auth_router",
    "users_router",
    "services_router",
    "eligibility_router",
    "discovery_router",
    "conversation_router",
    "documents_router",
]
