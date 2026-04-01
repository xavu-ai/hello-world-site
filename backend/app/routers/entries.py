"""Entries API router with CRUD endpoints."""
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.entry import Entry
from app.schemas.entry import (
    EntryCreate,
    EntryListResponse,
    EntryResponse,
    EntryUpdate,
)

router = APIRouter(prefix="/api/v1/entries", tags=["entries"])


@router.get("", response_model=EntryListResponse)
async def list_entries(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[str, Depends(get_current_user)],
) -> EntryListResponse:
    """List entries owned by the authenticated contributor."""
    user_id = UUID(current_user)
    query = select(Entry).where(Entry.owner_id == user_id).order_by(Entry.created_at.desc())
    result = await db.execute(query)
    entries = list(result.scalars().all())
    
    return EntryListResponse(
        entries=[
            EntryResponse(
                id=e.id,
                title=e.title,
                content=e.content,
                owner_id=e.owner_id,
                created_at=e.created_at,
                updated_at=e.updated_at,
            )
            for e in entries
        ]
    )


@router.post("", response_model=EntryResponse, status_code=status.HTTP_201_CREATED)
async def create_entry(
    request: EntryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[str, Depends(get_current_user)],
) -> EntryResponse:
    """Create a new entry owned by the authenticated contributor."""
    user_id = UUID(current_user)
    now = datetime.now(timezone.utc)
    
    entry = Entry(
        title=request.title,
        content=request.content,
        owner_id=user_id,
        created_at=now,
        updated_at=now,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    
    return EntryResponse(
        id=entry.id,
        title=entry.title,
        content=entry.content,
        owner_id=entry.owner_id,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


@router.put("/{entry_id}", response_model=EntryResponse)
async def update_entry(
    entry_id: UUID,
    request: EntryUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[str, Depends(get_current_user)],
) -> EntryResponse:
    """Update an entry owned by the authenticated contributor."""
    user_id = UUID(current_user)
    
    query = select(Entry).where(Entry.id == entry_id)
    result = await db.execute(query)
    entry = result.scalar_one_or_none()
    
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Entry not found"},
        )
    
    if entry.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Not your entry"},
        )
    
    update_data = request.model_dump(exclude_unset=True)
    if "title" in update_data:
        entry.title = update_data["title"]
    if "content" in update_data:
        entry.content = update_data["content"]
    
    entry.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(entry)
    
    return EntryResponse(
        id=entry.id,
        title=entry.title,
        content=entry.content,
        owner_id=entry.owner_id,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


@router.delete("/{entry_id}")
async def delete_entry(
    entry_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[str, Depends(get_current_user)],
) -> dict[str, str]:
    """Delete an entry owned by the authenticated contributor."""
    user_id = UUID(current_user)
    
    query = select(Entry).where(Entry.id == entry_id)
    result = await db.execute(query)
    entry = result.scalar_one_or_none()
    
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Entry not found"},
        )
    
    if entry.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Not your entry"},
        )
    
    await db.delete(entry)
    await db.commit()
    
    return {"message": "Entry deleted"}
