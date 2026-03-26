from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    env: str = "development"
    static_dir: str = "static"
    allowed_hosts: List[str] = ["*"]
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # CORS
    cors_origins: List[str] = ["*"]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Re-export for backwards compatibility
from .storage import get_storage_settings, StorageSettings

__all__ = ["Settings", "get_settings", "StorageSettings", "get_storage_settings"]
