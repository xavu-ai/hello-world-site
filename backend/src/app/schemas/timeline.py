"""Pydantic schemas for timeline API."""
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TimelineCreate(BaseModel):
    """Schema for creating a timeline entry."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    metadata: Optional[dict] = None


class TimelineUpdate(BaseModel):
    """Schema for updating a timeline entry."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    metadata: Optional[dict] = None


class TimelineResponse(BaseModel):
    """Schema for timeline entry response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    title: str
    description: Optional[str] = None
    timestamp: datetime
    user_id: UUID
    metadata: Optional[dict] = None

    @model_validator(mode="wrap")
    @classmethod
    def extract_metadata(cls, data: Any, info: Any) -> Any:
        """Extract metadata from ORM object (which stores it as meta_data)."""
        if hasattr(data, "meta_data"):
            data.metadata = data.meta_data
        return data


class TimelineListResponse(BaseModel):
    """Schema for paginated timeline list response."""

    items: list[TimelineResponse]
    total: int
    skip: int
    limit: int
