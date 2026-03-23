"""Pytest configuration and fixtures."""
from collections.abc import AsyncGenerator

import pytest
from app.db.base import Base
from app.db.deps import get_db
from app.main import app
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Use an in-memory SQLite for async tests with aiosqlite
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override get_db with test database."""
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def setup_database() -> AsyncGenerator[None, None]:
    """Create and drop tables for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client fixture."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
