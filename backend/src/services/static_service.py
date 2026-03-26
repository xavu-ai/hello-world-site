from pathlib import Path
from src.config import get_settings
from src.exceptions import FileNotFoundError, DirectoryTraversalError


class StaticFileService:
    def __init__(self, static_dir: Path | None = None):
        if static_dir:
            self.static_dir = static_dir
        else:
            settings = get_settings()
            self.static_dir = Path(settings.STATIC_DIR)
    
    def get_file(self, path: str) -> Path:
        """
        Get a static file by path, with directory traversal protection.
        """
        # Normalize and resolve the path
        requested_path = Path(path)
        
        # Block directory traversal attempts
        if ".." in path or path.startswith("/"):
            raise DirectoryTraversalError()
        
        # Build the full path
        file_path = self.static_dir / requested_path
        
        # Ensure the resolved path is within static_dir (realpath check)
        try:
            resolved = file_path.resolve()
            static_dir_resolved = self.static_dir.resolve()
            if not str(resolved).startswith(str(static_dir_resolved)):
                raise DirectoryTraversalError()
        except Exception:
            raise DirectoryTraversalError()
        
        # Check if file exists and is a file
        if not resolved.exists() or not resolved.is_file():
            raise FileNotFoundError(str(path))
        
        return resolved
    
    def file_exists(self, path: str) -> bool:
        """Check if a file exists."""
        try:
            requested_path = Path(path)
            if ".." in path or path.startswith("/"):
                return False
            file_path = (self.static_dir / requested_path).resolve()
            static_dir_resolved = self.static_dir.resolve()
            if not str(file_path).startswith(str(static_dir_resolved)):
                return False
            return file_path.exists() and file_path.is_file()
        except Exception:
            return False
