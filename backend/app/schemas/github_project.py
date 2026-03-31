"""Pydantic schemas for GitHub projects."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreateRequest(BaseModel):
    """Schema for creating a new GitHub project."""

    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: str | None = Field(None, description="Project description")
    owner: str = Field(..., min_length=1, max_length=100, description="GitHub owner/repo or organization")
    settings: dict[str, Any] = Field(default_factory=dict, description="Project settings")
    include_issues: bool = Field(True, description="Include issue tracking")
    include_wiki: bool = Field(False, description="Include wiki")


class ProjectResponse(BaseModel):
    """Schema for GitHub project response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    github_id: int | None = None
    name: str
    description: str | None = None
    owner: str
    url: str | None = None
    state: str
    settings: dict[str, Any] = Field(default_factory=dict)
    error_message: str | None = None
    created_by: str
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    """Schema for paginated list of GitHub projects."""

    items: list[ProjectResponse]
    total: int
    skip: int
    limit: int
