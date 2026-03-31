"""Pydantic schemas for file operations."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """Response schema for file upload."""

    id: UUID
    filename: str
    original_name: str
    mime_type: str
    size_bytes: int
    download_url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FileMetadata(BaseModel):
    """Schema for file metadata."""

    id: UUID
    filename: str
    original_name: str
    mime_type: str
    size_bytes: int
    checksum: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    uploaded_by: Optional[UUID] = None

    model_config = {"from_attributes": True}


class FileUploadRequest(BaseModel):
    """Request schema for file upload with optional expiration."""

    expires_in: Optional[int] = Field(
        default=None,
        description="Expiration time in hours. If None, file never expires.",
        ge=1,
        le=8760,  # Max 1 year
    )


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error: str
    message: str
    details: Optional[dict] = None
