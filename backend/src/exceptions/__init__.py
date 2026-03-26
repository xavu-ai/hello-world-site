from fastapi import HTTPException


class StaticFileError(HTTPException):
    pass


class FileNotFoundError(StaticFileError):
    def __init__(self, path: str = None):
        self.path = path
        detail = f"File not found: {path}" if path else "File not found"
        super().__init__(status_code=404, detail=detail)


class PathTraversalError(StaticFileError):
    """Raised when a path traversal attempt is detected."""
    def __init__(self, message: str = "Access denied"):
        self.message = message
        super().__init__(status_code=403, detail=message)


class DirectoryTraversalError(PathTraversalError):
    """Alias for PathTraversalError for backwards compatibility."""
    pass


class InvalidPathError(StaticFileError):
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid path")


# Import from file_exceptions for backwards compatibility
from .file_exceptions import (
    FileException,
    FileNotFoundError as FileOpNotFoundError,
    FileTooLargeError,
    InvalidFileTypeError,
    StorageError,
    DatabaseError,
)

__all__ = [
    "StaticFileError",
    "FileNotFoundError",
    "PathTraversalError",
    "DirectoryTraversalError",
    "InvalidPathError",
    "FileException",
    "FileOpNotFoundError",
    "FileTooLargeError",
    "InvalidFileTypeError",
    "StorageError",
    "DatabaseError",
]
