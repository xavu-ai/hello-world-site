"""Unit tests for GitHub project service."""
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.models.github_project import GitHubProject, ProjectState
from app.schemas.github_project import ProjectCreateRequest
from app.services import github_project_service


@pytest.fixture
def user_id() -> str:
    """Fixture for user ID."""
    return str(uuid4())


@pytest.fixture
def project_id() -> str:
    """Fixture for project ID."""
    return str(uuid4())


@pytest.fixture
def project_create_data() -> ProjectCreateRequest:
    """Fixture for project creation data."""
    return ProjectCreateRequest(
        name="Test Project",
        description="A test project",
        owner="test-owner",
        include_issues=True,
        include_wiki=False,
    )


@pytest.fixture
def mock_github_client() -> MagicMock:
    """Fixture for mock GitHub client."""
    client = MagicMock()
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


class TestCreateProject:
    """Tests for create_project function."""

    @pytest.mark.asyncio
    async def test_create_project_without_github_token(
        self,
        db_session: MagicMock,
        project_create_data: ProjectCreateRequest,
        user_id: str,
    ) -> None:
        """Test creating a project when no GitHub token is configured."""
        # Patch get_github_client to raise ValueError (no token)
        with patch(
            "app.services.github_project_service.get_github_client",
            side_effect=ValueError("No token"),
        ):
            project = await github_project_service.create_project(
                db_session,
                project_create_data,
                user_id=user_id,
            )

        assert project.name == "Test Project"
        assert project.description == "A test project"
        assert project.owner == "test-owner"
        assert project.state == ProjectState.PENDING
        assert project.created_by == user_id
        db_session.add.assert_called_once()
        db_session.commit.assert_called()
        db_session.refresh.assert_called()

    @pytest.mark.asyncio
    async def test_create_project_with_github_success(
        self,
        db_session: MagicMock,
        project_create_data: ProjectCreateRequest,
        user_id: str,
        mock_github_client: MagicMock,
    ) -> None:
        """Test creating a project with successful GitHub API call."""
        project = await github_project_service.create_project(
            db_session,
            project_create_data,
            user_id=user_id,
            github_client=mock_github_client,
        )

        assert project.name == "Test Project"
        assert project.github_id == 123456
        assert project.url == "https://github.com/users/test-owner/projects/123456"
        assert project.state == ProjectState.ACTIVE
        mock_github_client.create_project.assert_called_once_with(
            name="Test Project",
            description="A test project",
            owner="test-owner",
            include_issues=True,
            include_wiki=False,
        )


class TestGetProject:
    """Tests for get_project function."""

    @pytest.mark.asyncio
    async def test_get_project_found(
        self,
        db_session: MagicMock,
        project_id: str,
    ) -> None:
        """Test getting an existing project."""
        mock_project = MagicMock(spec=GitHubProject)
        mock_project.id = project_id
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_project
        db_session.execute.return_value = mock_result

        project = await github_project_service.get_project(db_session, uuid4())

        assert project == mock_project
        db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_project_not_found(
        self,
        db_session: MagicMock,
    ) -> None:
        """Test getting a non-existent project."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        db_session.execute.return_value = mock_result

        project = await github_project_service.get_project(db_session, uuid4())

        assert project is None


class TestListProjects:
    """Tests for list_projects function."""

    @pytest.mark.asyncio
    async def test_list_projects_empty(
        self,
        db_session: MagicMock,
    ) -> None:
        """Test listing projects when none exist."""
        call_count = [0]

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 0

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars

        async def execute_side_effect(*args):
            call_count[0] += 1
            if call_count[0] == 1:
                return mock_count_result
            return mock_result

        db_session.execute.side_effect = execute_side_effect

        projects, total = await github_project_service.list_projects(db_session)

        assert total == 0
        assert projects == []


class TestDeleteProject:
    """Tests for delete_project function."""

    @pytest.mark.asyncio
    async def test_delete_project_not_found(
        self,
        db_session: MagicMock,
    ) -> None:
        """Test deleting a non-existent project raises error."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        db_session.execute.return_value = mock_result

        with pytest.raises(
            github_project_service.GitHubProjectServiceError,
            match="not found",
        ):
            await github_project_service.delete_project(db_session, uuid4())

    @pytest.mark.asyncio
    async def test_delete_project_success(
        self,
        db_session: MagicMock,
        project_id: str,
    ) -> None:
        """Test deleting an existing project."""
        mock_project = MagicMock(spec=GitHubProject)
        mock_project.id = project_id
        mock_project.github_id = None  # No GitHub ID, local only
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_project
        db_session.execute.return_value = mock_result

        result = await github_project_service.delete_project(db_session, uuid4())

        assert result is True
        db_session.delete.assert_called_once_with(mock_project)
        db_session.commit.assert_called()
