from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import settings
from database import get_db
from api.auth import router as auth_router
from api.users import router as users_router
from api.services import router as services_router
from api.eligibility import router as eligibility_router
from api.discovery import router as discovery_router
from api.conversation import router as conversation_router
from api.documents import router as documents_router
from api.analytics import router as analytics_router
from api.accessibility import router as accessibility_router
from api.speech import router as speech_router

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API services for AccessGov AI — Public Service Access Platform & Document Intelligence Engine",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS (Cross-Origin Resource Sharing) Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers under /api/v1
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(services_router, prefix=settings.API_V1_STR)
app.include_router(eligibility_router, prefix=settings.API_V1_STR)
app.include_router(discovery_router, prefix=settings.API_V1_STR)
app.include_router(conversation_router, prefix=settings.API_V1_STR)
app.include_router(documents_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(accessibility_router, prefix=settings.API_V1_STR)
app.include_router(speech_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def read_root():
    """
    Root API endpoint returning basic platform details.
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "operational",
        "documentation": "/docs"
    }


@app.get("/health", tags=["System"])
@app.get(f"{settings.API_V1_STR}/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """
    System Health Endpoint.
    Performs a database connectivity check executing 'SELECT 1'.
    Returns status operational if connection succeeds, otherwise 503 Service Unavailable.
    """
    try:
        # Perform DB ping check
        result = db.execute(text("SELECT 1")).scalar()
        if result == 1:
            return {
                "status": "healthy",
                "database": "connected",
                "project": settings.PROJECT_NAME,
                "version": settings.VERSION
            }
        else:
            raise Exception("Unexpected query response from database")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connectivity health check failed: {str(e)}"
        )