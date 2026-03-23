"""Prompt submission endpoints."""
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.db.deps import DbDep
from app.schemas.prompt import PromptCreate, PromptList, PromptResponse
from app.services import prompt_service

router = APIRouter()


@router.post(
    "",
    response_model=PromptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new prompt",
)
async def create_prompt(db: DbDep, prompt_in: PromptCreate) -> PromptResponse:
    """Submit a new prompt for AI processing.

    Args:
        db: Database session
        prompt_in: Prompt creation data

    Returns:
        Created prompt with ID and status
    """
    prompt = await prompt_service.create_prompt(db, prompt_in)
    return PromptResponse.model_validate(prompt)


@router.get(
    "/{prompt_id}",
    response_model=PromptResponse,
    summary="Get prompt status and result",
)
async def get_prompt(db: DbDep, prompt_id: UUID) -> PromptResponse:
    """Get a prompt by ID with its current status and result.

    Args:
        db: Database session
        prompt_id: UUID of the prompt

    Returns:
        Prompt details

    Raises:
        HTTPException: If prompt not found
    """
    prompt = await prompt_service.get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt with ID {prompt_id} not found",
        )
    return PromptResponse.model_validate(prompt)


@router.get(
    "",
    response_model=PromptList,
    summary="List all prompts",
)
async def list_prompts(
    db: DbDep,
    skip: int = 0,
    limit: int = 100,
) -> PromptList:
    """List prompts with pagination.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Paginated list of prompts
    """
    prompts, total = await prompt_service.list_prompts(db, skip=skip, limit=limit)
    return PromptList(
        items=[PromptResponse.model_validate(p) for p in prompts],
        total=total,
        skip=skip,
        limit=limit,
    )
