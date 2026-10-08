from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# Create SQLAlchemy Database Engine
# pool_pre_ping=True enables automatic connection health checks before issuing queries
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG
)

# Create SessionLocal class factory for DB session creation per request
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for SQLAlchemy ORM models
Base = declarative_base()


def get_db() -> Generator:
    """
    FastAPI Dependency to yield a database session per request.
    Ensures connection is cleanly closed after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
