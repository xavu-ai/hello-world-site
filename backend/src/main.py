"""FastAPI application entry point for static file hosting."""
import hashlib
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    yield


app = FastAPI(
    title="Static File Hosting Service",
    description="A simple static file hosting service with FastAPI",
    version="1.0.0",
    lifespan=lifespan,
)

# Add GZip middleware for compression
if settings.ENABLE_GZIP:
    app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.get("/")
async def serve_index() -> FileResponse:
    """Serve the index.html file at root."""
    index_path = Path(settings.STATIC_DIR) / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_path, media_type="text/html")


@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.get("/static/{path:path}")
async def serve_static(path: str, request: Request) -> Response:
    """Serve static files with proper MIME types and caching headers."""
    # Security: prevent path traversal
    if ".." in path or path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid path")

    file_path = Path(settings.STATIC_DIR) / path

    # Security: ensure the resolved path is within STATIC_DIR
    try:
        file_path = file_path.resolve()
        static_dir = Path(settings.STATIC_DIR).resolve()
        if not str(file_path).startswith(str(static_dir)):
            raise HTTPException(status_code=400, detail="Invalid path")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid path")

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Determine MIME type
    mime_types = {
        ".html": "text/html",
        ".css": "text/css",
        ".js": "application/javascript",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".woff2": "font/woff2",
        ".woff": "font/woff",
        ".json": "application/json",
        ".xml": "application/xml",
    }

    ext = file_path.suffix.lower()
    media_type = mime_types.get(ext, "application/octet-stream")

    # Generate ETag
    file_content = file_path.read_bytes()
    etag = hashlib.md5(file_content).hexdigest()

    # Check If-None-Match header for caching
    if_none_match = request.headers.get("If-None-Match")
    if if_none_match and if_none_match == f'"{etag}"':
        return Response(status_code=304)

    # Build response with cache headers
    response = FileResponse(
        file_path,
        media_type=media_type,
        headers={
            "ETag": f'"{etag}"',
            "Cache-Control": f"public, max-age={settings.MAX_AGE_SECONDS}",
        },
    )
    return response


# Mount additional static files directory if needed
static_dir = Path(settings.STATIC_DIR)
if static_dir.exists():
    app.mount("/files", StaticFiles(directory=str(static_dir)), name="static_files")
