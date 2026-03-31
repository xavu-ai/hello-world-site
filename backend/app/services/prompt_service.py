"""Prompt service for business logic."""
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prompt import Prompt
from app.schemas.prompt import PromptCreate


async def create_prompt(session: AsyncSession, prompt_data: PromptCreate) -> Prompt:
    """Create a new prompt.

    Args:
        session: Database session
        prompt_data: Prompt creation data

    Returns:
        Created prompt instance
    """
    prompt = Prompt(content=prompt_data.content)
    session.add(prompt)
    await session.commit()
    await session.refresh(prompt)
    return prompt


async def get_prompt(session: AsyncSession, prompt_id: UUID) -> Prompt | None:
    """Get a prompt by ID.

    Args:
        session: Database session
        prompt_id: UUID of the prompt

    Returns:
        Prompt if found, None otherwise
    """
    result = await session.execute(select(Prompt).where(Prompt.id == str(prompt_id)))
    return result.scalar_one_or_none()


async def list_prompts(
    session: AsyncSession, skip: int = 0, limit: int = 100
) -> tuple[list[Prompt], int]:
    """List prompts with pagination.

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Tuple of (list of prompts, total count)
    """
    # Get total count
    total_result = await session.execute(select(func.count()).select_from(Prompt))
    total = total_result.scalar() or 0

    # Get paginated results
    result = await session.execute(
        select(Prompt).order_by(Prompt.created_at.desc()).offset(skip).limit(limit)
    )
    prompts = list(result.scalars().all())

    return prompts, total
