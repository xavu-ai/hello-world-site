"""Configuration management with environment variables."""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    STATIC_DIR: str = "/app/src/static"
    LOG_LEVEL: Literal["debug", "info", "warning", "error"] = "info"
    ENABLE_GZIP: bool = True
    MAX_AGE_SECONDS: int = 3600
    CORS_ORIGINS: str = "*"
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
