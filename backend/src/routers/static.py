from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from pathlib import Path
from src.config import get_settings
from src.services.static_service import StaticFileService

router = APIRouter()
service = StaticFileService()
settings = get_settings()
STATIC_DIR = Path(settings.STATIC_DIR)


@router.get("/")
async def serve_index():
    """Serve index.html"""
    return FileResponse(STATIC_DIR / "index.html")


@router.get("/{path:path}")
async def serve_static_file(path: str, request: Request):
    """
    Serve static file by path with SPA fallback.
    """
    # Check if the requested file exists
    if service.file_exists(path):
        file_path = service.get_file(path)
        return FileResponse(file_path)
    
    # SPA fallback - serve index.html for client-side routing
    return FileResponse(STATIC_DIR / "index.html")
