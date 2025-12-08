"""LimeStar Database Connection and Session Management"""

from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

from app.config import settings

# Create engine
# For SQLite, we need connect_args to allow multi-threading
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, echo=settings.DEBUG)


def init_db() -> None:
    """Initialize database tables"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session for dependency injection"""
    with Session(engine) as session:
        yield session
