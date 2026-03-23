"""Integration tests for GitHub projects API."""
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.base import Base
from app.db.deps import get_db
from app.integrations.github_client import GitHubClient
from app.main import app
from app.models.github_project import GitHubProject, ProjectState
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


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


async def override_get_db() -> MagicMock:
    """Override get_db with test database."""
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def setup_database() -> MagicMock:
    """Create and drop tables for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client() -> MagicMock:
    """Async HTTP client fixture."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def user_id() -> str:
    """Fixture for user ID."""
    return str(uuid4())


@pytest.fixture
def mock_github_client() -> MagicMock:
    """Fixture for mock GitHub client."""
    client = MagicMock(spec=GitHubClient)
    client.create_project = AsyncMock(
        return_value={
            "id": 123456,
            "name": "Test Project",
            "html_url": "https://github.com/users/test-owner/projects/123456",
            "body": "A test project",
        }
    )
    client.delete_project = AsyncMock()
    return client


class TestCreateGitHubProject:
    """Tests for POST /api/v1/github/projects endpoint."""

    @pytest.mark.asyncio
    async def test_create_project_without_github_token(
        self,
        client: MagicMock,
        user_id: str,
    ) -> None:
        """Test creating a project without GitHub token configured."""
        with patch(
            "app.services.github_project_service.get_github_client",
            side_effect=ValueError("GitHub token is required"),
        ):
            response = await client.post(
                "/api/v1/github/projects",
                json={
                    "name": "Test Project",
                    "description": "A test project",
                    "owner": "test-owner",
                },
                headers={"x-user-id": user_id},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["description"] == "A test project"
        assert data["owner"] == "test-owner"
        assert data["state"] == "pending"

    @pytest.mark.asyncio
    async def test_create_project_with_github_success(
        self,
        client: MagicMock,
        user_id: str,
        mock_github_client: MagicMock,
    ) -> None:
        """Test creating a project with successful GitHub API call."""
        with patch(
            "app.services.github_project_service.get_github_client",
            return_value=mock_github_client,
        ):
            response = await client.post(
                "/api/v1/github/projects",
                json={
                    "name": "Test Project",
                    "description": "A test project",
                    "owner": "test-owner",
                    "include_issues": True,
                    "include_wiki": False,
                },
                headers={"x-user-id": user_id},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["state"] == "active"
        assert data["github_id"] == 123456
        assert data["url"] == "https://github.com/users/test-owner/projects/123456"


class TestListGitHubProjects:
    """Tests for GET /api/v1/github/projects endpoint."""

    @pytest.mark.asyncio
    async def test_list_projects_empty(
        self,
        client: MagicMock,
    ) -> None:
        """Test listing projects when none exist."""
        response = await client.get("/api/v1/github/projects")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["skip"] == 0
        assert data["limit"] == 100

    @pytest.mark.asyncio
    async def test_list_projects_with_pagination(
        self,
        client: MagicMock,
        user_id: str,
    ) -> None:
        """Test listing projects with pagination parameters."""
        # Create a project first
        with patch(
            "app.services.github_project_service.get_github_client",
            side_effect=ValueError("GitHub token is required"),
        ):
            await client.post(
                "/api/v1/github/projects",
                json={
                    "name": "Test Project",
                    "owner": "test-owner",
                },
                headers={"x-user-id": user_id},
            )

        response = await client.get(
            "/api/v1/github/projects",
            params={"skip": 0, "limit": 10},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] == 1


class TestGetGitHubProject:
    """Tests for GET /api/v1/github/projects/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_project_not_found(
        self,
        client: MagicMock,
    ) -> None:
        """Test getting a non-existent project."""
        fake_id = str(uuid4())
        response = await client.get(f"/api/v1/github/projects/{fake_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestDeleteGitHubProject:
    """Tests for DELETE /api/v1/github/projects/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_project_not_found(
        self,
        client: MagicMock,
    ) -> None:
        """Test deleting a non-existent project."""
        fake_id = str(uuid4())
        response = await client.delete(f"/api/v1/github/projects/{fake_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
