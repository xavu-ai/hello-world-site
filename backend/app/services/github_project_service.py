"""GitHub project service for business logic."""
import logging
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.github_client import GitHubClient, GitHubAPIError, get_github_client
from app.models.github_project import GitHubProject, ProjectState
from app.schemas.github_project import ProjectCreateRequest

logger = logging.getLogger(__name__)


class GitHubProjectServiceError(Exception):
    """Base exception for GitHub project service errors."""

    pass


class ProjectCreationError(GitHubProjectServiceError):
    """Error creating GitHub project."""

    pass


async def create_project(
    session: AsyncSession,
    project_data: ProjectCreateRequest,
    user_id: str,
    github_client: GitHubClient | None = None,
) -> GitHubProject:
    """Create a new GitHub project.

    Args:
        session: Database session
        project_data: Project creation data
        user_id: ID of the user creating the project
        github_client: Optional GitHub client (for testing)

    Returns:
        Created GitHubProject instance

    Raises:
        ProjectCreationError: If project creation fails
    """
    # Create local record first
    project = GitHubProject(
        name=project_data.name,
        description=project_data.description,
        owner=project_data.owner,
        settings=project_data.settings,
        state=ProjectState.PENDING,
        created_by=user_id,
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)

    # Try to create on GitHub if client is available
    if github_client is None:
        try:
            github_client = get_github_client()
        except ValueError:
            # No GitHub token configured, just return the local record
            logger.warning("No GitHub token configured, project created locally only")
            return project

    try:
        # Update state to creating
        project.state = ProjectState.CREATING
        await session.commit()

        # Create on GitHub
        gh_project = await github_client.create_project(
            name=project_data.name,
            description=project_data.description,
            owner=project_data.owner,
            include_issues=project_data.include_issues,
            include_wiki=project_data.include_wiki,
        )

        # Update with GitHub response
        project.github_id = gh_project["id"]
        project.url = gh_project["html_url"]
        project.state = ProjectState.ACTIVE
        await session.commit()
        await session.refresh(project)

        return project

    except GitHubAPIError as e:
        project.state = ProjectState.FAILED
        project.error_message = str(e)
        await session.commit()
        await session.refresh(project)
        raise ProjectCreationError(f"Failed to create GitHub project: {e}") from e


async def get_project(
    session: AsyncSession,
    project_id: UUID,
) -> GitHubProject | None:
    """Get a GitHub project by ID.

    Args:
        session: Database session
        project_id: UUID of the project

    Returns:
        GitHubProject if found, None otherwise
    """
    result = await session.execute(
        select(GitHubProject).where(GitHubProject.id == str(project_id))
    )
    return result.scalar_one_or_none()


async def get_project_by_github_id(
    session: AsyncSession,
    github_id: int,
) -> GitHubProject | None:
    """Get a GitHub project by GitHub project ID.

    Args:
        session: Database session
        github_id: GitHub project ID

    Returns:
        GitHubProject if found, None otherwise
    """
    result = await session.execute(
        select(GitHubProject).where(GitHubProject.github_id == github_id)
    )
    return result.scalar_one_or_none()


async def list_projects(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    user_id: str | None = None,
) -> tuple[list[GitHubProject], int]:
    """List GitHub projects with pagination.

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        user_id: Optional filter by user ID

    Returns:
        Tuple of (list of projects, total count)
    """
    # Base query
    query = select(GitHubProject)

    if user_id:
        query = query.where(GitHubProject.created_by == user_id)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    result = await session.execute(
        query.order_by(GitHubProject.created_at.desc()).offset(skip).limit(limit)
    )
    projects = list(result.scalars().all())

    return projects, total


async def delete_project(
    session: AsyncSession,
    project_id: UUID,
    github_client: GitHubClient | None = None,
) -> bool:
    """Delete a GitHub project.

    Args:
        session: Database session
        project_id: UUID of the project
        github_client: Optional GitHub client (for testing)

    Returns:
        True if deleted successfully

    Raises:
        GitHubProjectServiceError: If project not found or deletion fails
    """
    project = await get_project(session, project_id)
    if not project:
        raise GitHubProjectServiceError(f"Project with ID {project_id} not found")

    # Delete from GitHub if we have a github_id
    if project.github_id and github_client is not None:
        try:
            await github_client.delete_project(project.github_id)
        except GitHubAPIError as e:
            logger.warning(f"Failed to delete GitHub project {project.github_id}: {e}")
            # Continue to delete local record even if GitHub deletion fails

    # Mark as deleted locally
    project.state = ProjectState.DELETED
    await session.commit()

    # Actually delete the record
    await session.delete(project)
    await session.commit()

    return True
