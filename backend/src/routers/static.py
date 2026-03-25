"""Static file serving router."""

import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import FileResponse

from ..config import Settings, get_settings
from ..exceptions import FileNotFoundError, PathTraversalError

logger = structlog.get_logger()

router = APIRouter(tags=["static"])

# MIME type mapping for common file extensions
MIME_TYPES = {
    ".html": "text/html",
    ".htm": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".mjs": "application/javascript",
    ".json": "application/json",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
    ".eot": "application/vnd.ms-fontobject",
    ".webp": "image/webp",
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".xml": "application/xml",
    ".webmanifest": "application/manifest+json",
}


def get_mime_type(file_path: Path) -> str:
    """Determine MIME type based on file extension."""
    return MIME_TYPES.get(file_path.suffix.lower(), "application/octet-stream")


def generate_etag(file_path: Path) -> str:
    """Generate ETag for a file based on its mtime and size."""
    stat = file_path.stat()
    etag_content = f"{stat.st_mtime}:{stat.st_size}"
    return hashlib.md5(etag_content.encode()).hexdigest()


def check_path_traversal(requested_path: Path, static_dir: Path) -> None:
    """Check for path traversal attempts and raise exception if detected."""
    # Resolve the requested path and check if it's within static_dir
    try:
        resolved_path = requested_path.resolve()
        static_dir_resolved = static_dir.resolve()
    except (OSError, ValueError):
        raise PathTraversalError("Invalid path")

    # Check that the resolved path is within static_dir
    try:
        resolved_path.relative_to(static_dir_resolved)
    except ValueError:
        raise PathTraversalError("Access denied")


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get(
    "/static/{path:path}",
    responses={
        200: {"description": "Static file"},
        403: {"description": "Path traversal attempt blocked"},
        404: {"description": "File not found"},
    },
)
async def serve_static_file(
    path: str,
    download: bool = Query(False, description="Force file download"),
    settings: Settings = Depends(get_settings),
) -> Response:
    """
    Serve static files from the configured static directory.

    - Validates path to prevent directory traversal attacks
    - Supports optional file download via ?download=1 query param
    - Returns proper Content-Type headers based on file extension
    - Generates ETag for client-side caching
    """
    # Construct the full file path
    requested_path = settings.static_dir / path

    # Check for path traversal
    check_path_traversal(requested_path, settings.static_dir)

    # Check if file exists
    if not requested_path.exists():
        raise FileNotFoundError(path)

    if not requested_path.is_file():
        raise FileNotFoundError(path)

    # Get MIME type
    content_type = get_mime_type(requested_path)

    # Generate ETag
    etag = generate_etag(requested_path)

    # Determine if file should be downloaded or displayed
    content_disposition = "attachment" if download else None

    logger.info(
        "serving_static_file",
        path=path,
        content_type=content_type,
    )

    return FileResponse(
        path=requested_path,
        media_type=content_type,
        filename=requested_path.name if download else None,
        content_disposition=content_disposition,
        headers={"ETag": etag},
    )


@router.get("/", response_class=FileResponse)
async def serve_index(settings: Settings = Depends(get_settings)) -> Response:
    """
    Serve index.html as the default page.

    Returns index.html from the static directory root.
    """
    index_path = settings.static_dir / "index.html"

    if not index_path.exists():
        raise FileNotFoundError("index.html")

    return FileResponse(
        path=index_path,
        media_type="text/html",
    )
