"""Configuration settings for the static file server."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Server settings
    host: str = "0.0.0.0"
    port: int = 3000
    reload: bool = False

    # Static files settings
    static_dir: Path = Path("/app/static")
    static_url: str = "/static"

    # CORS settings (if needed)
    cors_origins: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
