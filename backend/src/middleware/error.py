"""Global exception handlers for the static file server."""

import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from ..exceptions import FileNotFoundError, PathTraversalError
from ..schemas.response import ErrorResponse

logger = structlog.get_logger()


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""

    @app.exception_handler(PathTraversalError)
    async def path_traversal_handler(
        request: Request, exc: PathTraversalError
    ) -> JSONResponse:
        """Handle path traversal attempts."""
        logger.warning("path_traversal_blocked", path=request.url.path)
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponse(
                error="PATH_TRAVERSAL",
                detail=exc.message,
            ).model_dump(),
        )

    @app.exception_handler(FileNotFoundError)
    async def file_not_found_handler(
        request: Request, exc: FileNotFoundError
    ) -> JSONResponse:
        """Handle file not found errors."""
        logger.info("file_not_found", path=exc.path)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                error="FILE_NOT_FOUND",
                detail="File not found",
            ).model_dump(),
        )

    @app.exception_handler(PermissionError)
    async def permission_error_handler(
        request: Request, exc: PermissionError
    ) -> JSONResponse:
        """Handle file permission errors."""
        logger.error("permission_denied", path=request.url.path)
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponse(
                error="ACCESS_DENIED",
                detail="Access denied",
            ).model_dump(),
        )
