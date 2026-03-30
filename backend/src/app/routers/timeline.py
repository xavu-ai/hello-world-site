"""Timeline API router with CRUD endpoints."""
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.timeline import TimelineEntry
from app.schemas.timeline import (
    TimelineCreate,
    TimelineListResponse,
    TimelineResponse,
    TimelineUpdate,
)

router = APIRouter(prefix="/api/v1/timeline", tags=["timeline"])


@router.get("", response_model=TimelineListResponse)
async def list_timeline_entries(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> TimelineListResponse:
    """List timeline entries with pagination."""
    # Get total count
    count_query = select(func.count()).select_from(TimelineEntry)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated items
    query = (
        select(TimelineEntry)
        .order_by(TimelineEntry.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    items = list(result.scalars().all())

    return TimelineListResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("", response_model=TimelineResponse, status_code=status.HTTP_201_CREATED)
async def create_timeline_entry(
    entry: TimelineCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TimelineEntry:
    """Create a new timeline entry."""
    # For now, use a placeholder user_id since auth isn't fully implemented
    # In production, this would come from get_current_user dependency
    from uuid import uuid4

    db_entry = TimelineEntry(
        title=entry.title,
        description=entry.description,
        meta_data=entry.metadata,
        timestamp=datetime.now(timezone.utc),
        user_id=uuid4(),  # Placeholder
    )
    db.add(db_entry)
    await db.commit()
    await db.refresh(db_entry)
    return db_entry


@router.get("/{entry_id}", response_model=TimelineResponse)
async def read_timeline_entry(
    entry_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TimelineEntry:
    """Read a single timeline entry by ID."""
    query = select(TimelineEntry).where(TimelineEntry.id == entry_id)
    result = await db.execute(query)
    entry = result.scalar_one_or_none()

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Timeline entry {entry_id} not found"},
        )

    return entry


@router.put("/{entry_id}", response_model=TimelineResponse)
async def update_timeline_entry(
    entry_id: UUID,
    entry_update: TimelineUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TimelineEntry:
    """Update an existing timeline entry."""
    query = select(TimelineEntry).where(TimelineEntry.id == entry_id)
    result = await db.execute(query)
    entry = result.scalar_one_or_none()

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Timeline entry {entry_id} not found"},
        )

    update_data = entry_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)

    await db.commit()
    await db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timeline_entry(
    entry_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a timeline entry."""
    query = select(TimelineEntry).where(TimelineEntry.id == entry_id)
    result = await db.execute(query)
    entry = result.scalar_one_or_none()

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Timeline entry {entry_id} not found"},
        )

    await db.delete(entry)
    await db.commit()
