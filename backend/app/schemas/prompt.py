"""Pydantic schemas for prompts."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PromptCreate(BaseModel):
    """Schema for creating a new prompt."""

    content: str = Field(..., min_length=1, description="The user's prompt content")


class PromptResponse(BaseModel):
    """Schema for prompt response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    content: str
    status: str
    created_at: datetime
    updated_at: datetime
    result: str | None = None


class PromptList(BaseModel):
    """Schema for paginated list of prompts."""

    items: list[PromptResponse]
    total: int
    skip: int
    limit: int
