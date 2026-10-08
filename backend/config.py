import os
from pathlib import Path
from typing import List, Union, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings management using Pydantic Settings.
    Environment variables are automatically loaded from .env file.
    """
    # General API Configuration
    PROJECT_NAME: str = "AccessGov AI Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database Configuration (PostgreSQL)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "accessgov_user"
    POSTGRES_PASSWORD: str = "accessgov_secret_password"
    POSTGRES_DB: str = "accessgov_db"
    
    # Database URL override or dynamically constructed
    DATABASE_URL: str = Field(
        default="postgresql://accessgov_user:accessgov_secret_password@localhost:5432/accessgov_db",
        description="PostgreSQL Database Connection URL"
    )

    # Security & JWT Configuration
    SECRET_KEY: str = "accessgov_super_secret_jwt_key_change_in_production_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
	"http://localhost:3002",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
	"http://127.0.0.1:3002",
        "http://127.0.0.1:5173",
    ]

    # Session 3 RAG & Intelligence Settings
    CHROMA_DB_PATH: str = Field(
        default="C:/Users/HP/AccessGov-AI/backend/data/chroma",
        description="Path to local ChromaDB vector store"
    )
    EMBEDDING_MODEL: str = Field(
        default="all-MiniLM-L6-v2",
        description="HuggingFace SentenceTransformer embedding model name"
    )
    KNOWLEDGE_DATA_PATH: str = Field(
        default="C:/Users/HP/AccessGov-AI/datasets",
        description="Path to JSON knowledge datasets directory"
    )

    # Session 4 Google ADK & Gemini Agent Settings
    GEMINI_API_KEY: Optional[str] = Field(
        default=None,
        description="API Key for Google Gemini Generative AI Services"
    )
    GEMINI_MODEL: str = Field(
        default="gemini-2.5-flash",
        description="Google Gemini model identifier for conversational orchestration"
    )
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None, description="Google Identity Services OAuth client ID")
    AGENT_MEMORY_WINDOW: int = Field(
        default=10,
        description="Number of past conversation messages retained in agent memory"
    )
    AGENT_MAX_RETRIES: int = Field(
        default=2,
        description="Maximum retry attempts for LLM service invocation"
    )

    # Session 5 Document Intelligence Settings
    OCR_LANGUAGE: str = Field(
        default="en",
        description="Primary OCR language code"
    )
    MAX_UPLOAD_SIZE_MB: int = Field(
        default=10,
        description="Maximum allowed file upload size in megabytes"
    )
    DOCUMENT_STORAGE_PATH: str = Field(
        default="C:/Users/HP/AccessGov-AI/backend/storage/documents",
        description="Local directory for secure isolated document file storage"
    )
    OCR_CONFIDENCE_THRESHOLD: float = Field(
        default=0.60,
        description="Minimum confidence score threshold for valid document classification"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

# Keep cloned/demo copies isolated from the original project folder.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
settings.CHROMA_DB_PATH = str(_PROJECT_ROOT / "backend" / "data" / "chroma")
settings.KNOWLEDGE_DATA_PATH = str(_PROJECT_ROOT / "datasets")
settings.DOCUMENT_STORAGE_PATH = str(_PROJECT_ROOT / "backend" / "storage" / "documents")
