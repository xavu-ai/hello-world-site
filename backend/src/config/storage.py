"""Storage configuration for file hosting."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageSettings(BaseSettings):
    """Storage backend settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Storage path for uploaded files
    storage_path: Path = Field(default=Path("/app/storage"), validation_alias="STORAGE_PATH")
    
    # Maximum file size in bytes (default 100MB)
    max_file_size: int = Field(default=104857600, validation_alias="MAX_FILE_SIZE")
    
    # Allowed MIME types (comma-separated, supports wildcards)
    allowed_types: str = Field(default="image/*,application/pdf,text/*", validation_alias="ALLOWED_TYPES")
    
    # Database URL for file metadata
    database_url: Optional[str] = Field(default=None, validation_alias="DATABASE_URL")

    @property
    def allowed_mime_types(self) -> list[str]:
        """Parse allowed types string into a list."""
        return [t.strip() for t in self.allowed_types.split(",") if t.strip()]

    def is_type_allowed(self, mime_type: str) -> bool:
        """Check if a MIME type is allowed."""
        for allowed in self.allowed_mime_types:
            if allowed.endswith("/*"):
                # Wildcard matching (e.g., "image/*" matches "image/png")
                prefix = allowed[:-1]
                if mime_type.startswith(prefix):
                    return True
            elif allowed == mime_type:
                return True
        return False


# Global storage settings instance
_storage_settings: Optional[StorageSettings] = None


def get_storage_settings() -> StorageSettings:
    """Get or create storage settings singleton."""
    global _storage_settings
    if _storage_settings is None:
        _storage_settings = StorageSettings()
    return _storage_settings


def get_storage_path() -> Path:
    """Get the storage path, creating it if necessary."""
    settings = get_storage_settings()
    settings.storage_path.mkdir(parents=True, exist_ok=True)
    return settings.storage_path
