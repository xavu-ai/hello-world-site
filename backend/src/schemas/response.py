"""Response schemas for the static file server."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: str = Field(..., description="Error code")
    detail: str = Field(..., description="Human-readable error message")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(..., description="Current server timestamp")


class StaticFileResponse(BaseModel):
    """Metadata response for static file operations."""

    path: str = Field(..., description="File path")
    size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="MIME type")
