"""SQLAlchemy engine, session factory and declarative base."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import get_settings

class Base(DeclarativeBase):
    """Base class for all ORM models."""

settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

def get_db():
    """Yield one request-scoped session and always release its connection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
