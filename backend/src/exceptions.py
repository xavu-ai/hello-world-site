"""Custom exceptions for the static file server."""


class PathTraversalError(Exception):
    """Raised when a path traversal attack is detected."""

    def __init__(self, message: str = "Access denied"):
        self.message = message
        super().__init__(self.message)


class FileNotFoundError(Exception):
    """Raised when a requested file is not found."""

    def __init__(self, path: str):
        self.path = path
        self.message = f"File not found: {path}"
        super().__init__(self.message)
