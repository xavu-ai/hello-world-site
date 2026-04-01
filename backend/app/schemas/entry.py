"""Pydantic schemas for entries endpoints."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EntryCreate(BaseModel):
    """Schema for creating an entry."""

    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = None


class EntryUpdate(BaseModel):
    """Schema for updating an entry."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None


class EntryResponse(BaseModel):
    """Schema for entry response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    content: Optional[str] = None
    owner_id: UUID
    created_at: datetime
    updated_at: datetime


class EntryListResponse(BaseModel):
    """Schema for entries list response."""

    entries: list[EntryResponse]
