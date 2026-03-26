"""Static file serving router."""

import hashlib
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
    try:
        resolved_path = requested_path.resolve()
        static_dir_resolved = static_dir.resolve()
    except (OSError, ValueError):
        raise PathTraversalError("Invalid path")

    try:
        resolved_path.relative_to(static_dir_resolved)
    except ValueError:
        raise PathTraversalError("Access denied")


def serve_file(
    relative_path: str,
    settings: Settings,
    download: bool = False,
) -> Response:
    """Helper to serve a file with proper headers and caching."""
    requested_path = settings.static_dir / relative_path
    check_path_traversal(requested_path, settings.static_dir)

    if not requested_path.exists():
        raise FileNotFoundError(relative_path)

    if not requested_path.is_file():
        raise FileNotFoundError(relative_path)

    content_type = get_mime_type(requested_path)
    etag = generate_etag(requested_path)

    content_disposition = "attachment" if download else None

    logger.info(
        "serving_static_file",
        path=relative_path,
        content_type=content_type,
    )

    return FileResponse(
        path=requested_path,
        media_type=content_type,
        filename=requested_path.name if download else None,
        content_disposition=content_disposition,
        headers={"ETag": etag},
    )


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}


@router.get("/")
async def serve_index(settings: Settings = Depends(get_settings)) -> Response:
    """Serve index.html as the default page."""
    return serve_file("index.html", settings)


@router.get("/css/{path:path}")
async def serve_css(path: str, settings: Settings = Depends(get_settings)) -> Response:
    """Serve CSS files."""
    return serve_file(f"css/{path}", settings)


@router.get("/js/{path:path}")
async def serve_js(path: str, settings: Settings = Depends(get_settings)) -> Response:
    """Serve JavaScript files."""
    return serve_file(f"js/{path}", settings)
