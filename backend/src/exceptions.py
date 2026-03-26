from fastapi import HTTPException


class StaticFileError(HTTPException):
    pass


class FileNotFoundError(StaticFileError):
    def __init__(self, path: str):
        super().__init__(status_code=404, detail=f"File not found: {path}")


class DirectoryTraversalError(StaticFileError):
    def __init__(self):
        super().__init__(status_code=403, detail="Access denied")


class InvalidPathError(StaticFileError):
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid path")
