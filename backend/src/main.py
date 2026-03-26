"""FastAPI application entry point for static file hosting."""
import hashlib
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from starlette.responses import FileResponse as StarletteFileResponse

from settings import get_settings

settings = get_settings()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class PathTraversalError(HTTPException):
    """Raised when path traversal is detected."""

    def __init__(self):
        super().__init__(status_code=403, detail="Path traversal detected")


class FileTooLargeError(HTTPException):
    """Raised when file exceeds size limit."""

    def __init__(self):
        super().__init__(status_code=413, detail="File too large")


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

# Add CORS middleware
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add GZip middleware for compression
if settings.ENABLE_GZIP:
    app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.exception_handler(PathTraversalError)
async def path_traversal_handler(request: Request, exc: PathTraversalError):
    """Handle path traversal errors."""
    return JSONResponse(status_code=403, content={"detail": exc.detail})


@app.exception_handler(FileTooLargeError)
async def file_too_large_handler(request: Request, exc: FileTooLargeError):
    """Handle file too large errors."""
    return JSONResponse(status_code=413, content={"detail": exc.detail})


@app.get("/")
async def serve_index(request: Request) -> Response:
    """Serve the index.html file at root."""
    index_path = Path(settings.STATIC_DIR) / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")

    # Check file size before reading
    file_size = index_path.stat().st_size
    if file_size > MAX_FILE_SIZE:
        raise FileTooLargeError()

    # Generate ETag with SHA-256
    file_content = index_path.read_bytes()
    etag = f'"{hashlib.sha256(file_content).hexdigest()}"'

    # Check If-None-Match header for caching
    if_none_match = request.headers.get("If-None-Match")
    if if_none_match and if_none_match == etag:
        return Response(status_code=304, headers={"ETag": etag})

    return StarletteFileResponse(
        path=str(index_path),
        media_type="text/html",
        headers={
            "ETag": etag,
            "Cache-Control": f"public, max-age={settings.MAX_AGE_SECONDS}",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
        },
    )


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
        raise PathTraversalError()

    file_path = Path(settings.STATIC_DIR) / path

    # Security: ensure the resolved path is within STATIC_DIR using is_relative_to
    try:
        file_path = file_path.resolve()
        static_dir = Path(settings.STATIC_DIR).resolve()
        if not file_path.is_relative_to(static_dir):
            raise PathTraversalError()
    except Exception:
        raise PathTraversalError()

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Check file size before reading
    file_size = file_path.stat().st_size
    if file_size > MAX_FILE_SIZE:
        raise FileTooLargeError()

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

    # Generate ETag with SHA-256
    file_content = file_path.read_bytes()
    etag = f'"{hashlib.sha256(file_content).hexdigest()}"'

    # Check If-None-Match header for caching
    if_none_match = request.headers.get("If-None-Match")
    if if_none_match and if_none_match == etag:
        return Response(status_code=304, headers={"ETag": etag})

    return StarletteFileResponse(
        path=str(file_path),
        media_type=media_type,
        headers={
            "ETag": etag,
            "Cache-Control": f"public, max-age={settings.MAX_AGE_SECONDS}",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
        },
    )
