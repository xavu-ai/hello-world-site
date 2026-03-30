"""Pytest fixtures for backend tests."""
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_db
from app.main import app
from app.models.timeline import Base, TimelineEntry

# Use SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture
async def async_engine():
    """Create test database engine."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async with TestAsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with overridden database dependency."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_timeline_data() -> dict[str, Any]:
    """Sample timeline data for tests."""
    return {
        "title": "Test Event",
        "description": "A test timeline entry",
        "metadata": {"key": "value"},
    }


@pytest.fixture
def sample_timeline_entry(db_session: AsyncSession) -> TimelineEntry:
    """Create a sample timeline entry in the database."""
    entry = TimelineEntry(
        id=uuid4(),
        title="Existing Event",
        description="An existing timeline entry",
        timestamp=datetime.utcnow(),
        user_id=uuid4(),
        metadata={"existing": True},
    )
    db_session.add(entry)
    # Don't commit yet - let test manage commit
    return entry
