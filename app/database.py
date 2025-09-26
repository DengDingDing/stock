"""
Database initialization and session management.

Sets up the asynchronous SQLAlchemy engine and session factory.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings

# Create an asynchronous engine for the given database URL.
# echo=True will log all SQL statements, useful for debugging.
async_engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Create a configured "AsyncSession" class.
# This is a factory for creating new AsyncSession objects.
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False, # Prevents SQLAlchemy from expiring objects after commit
)

# Base class for our ORM models.
# All model classes will inherit from this class.
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get a database session.

    Yields:
        An asynchronous database session.
    """
    async with AsyncSessionLocal() as session:
        yield session
