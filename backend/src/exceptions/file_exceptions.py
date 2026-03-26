"""Custom exceptions for file operations."""


class FileException(Exception):
    """Base exception for file operations."""
    pass


class FileNotFoundError(FileException):
    """Raised when a requested file is not found."""
    pass


class FileTooLargeError(FileException):
    """Raised when a file exceeds the maximum allowed size."""
    pass


class InvalidFileTypeError(FileException):
    """Raised when a file type is not allowed."""
    pass


class StorageError(FileException):
    """Raised when there is an error with the storage backend."""
    pass


class DatabaseError(FileException):
    """Raised when there is a database error."""
    pass
