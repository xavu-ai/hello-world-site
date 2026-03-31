"""GitHub project submission endpoints."""
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status

from app.db.deps import DbDep
from app.schemas.github_project import (
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectResponse,
)
from app.services import github_project_service

router = APIRouter()


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new GitHub project",
)
async def create_github_project(
    db: DbDep,
    project_in: ProjectCreateRequest,
    x_user_id: str = Header(..., description="User ID"),
) -> ProjectResponse:
    """Create a new GitHub project.

    Args:
        db: Database session
        project_in: Project creation data
        x_user_id: ID of the user creating the project (from auth header)

    Returns:
        Created project with ID and status
    """
    try:
        project = await github_project_service.create_project(
            db, project_in, user_id=x_user_id
        )
        return ProjectResponse.model_validate(project)
    except github_project_service.ProjectCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="List all GitHub projects",
)
async def list_github_projects(
    db: DbDep,
    skip: int = 0,
    limit: int = 100,
    x_user_id: str | None = Header(None, description="User ID for filtering"),
) -> ProjectListResponse:
    """List GitHub projects with pagination.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        x_user_id: Optional filter by user ID from header

    Returns:
        Paginated list of projects
    """
    projects, total = await github_project_service.list_projects(
        db, skip=skip, limit=limit, user_id=x_user_id
    )
    return ProjectListResponse(
        items=[ProjectResponse.model_validate(p) for p in projects],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get GitHub project details",
)
async def get_github_project(
    db: DbDep,
    project_id: UUID,
) -> ProjectResponse:
    """Get a GitHub project by ID.

    Args:
        db: Database session
        project_id: UUID of the project

    Returns:
        Project details

    Raises:
        HTTPException: If project not found
    """
    project = await github_project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )
    return ProjectResponse.model_validate(project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a GitHub project",
)
async def delete_github_project(
    db: DbDep,
    project_id: UUID,
) -> None:
    """Delete a GitHub project.

    Args:
        db: Database session
        project_id: UUID of the project

    Raises:
        HTTPException: If project not found or deletion fails
    """
    try:
        await github_project_service.delete_project(db, project_id)
    except github_project_service.GitHubProjectServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
