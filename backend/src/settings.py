"""Configuration management with environment variables."""
import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    STATIC_DIR: str = "/app/src/static"
    LOG_LEVEL: Literal["debug", "info", "warning", "error"] = "info"
    ENABLE_GZIP: bool = True
    MAX_AGE_SECONDS: int = 3600
    CORS_ORIGINS: str = ""  # Empty string instead of "*"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    ENVIRONMENT: Literal["development", "production"] = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def validate_cors_origins(cls, v: str) -> str:
        """Validate CORS_ORIGINS - reject '*' in production."""
        if not v:
            return ""
        origins = [o.strip() for o in v.split(",") if o.strip()]
        # Check for wildcard
        if "*" in origins:
            env = os.getenv("ENVIRONMENT", "development")
            if env == "production":
                raise ValueError("Wildcard '*' not allowed in CORS_ORIGINS in production")
        return v

    @field_validator("STATIC_DIR", mode="before")
    @classmethod
    def validate_static_dir(cls, v: str) -> str:
        """Validate STATIC_DIR exists and is readable."""
        if not v:
            raise ValueError("STATIC_DIR cannot be empty")
        path = Path(v)
        if not path.exists():
            raise ValueError(f"STATIC_DIR does not exist: {v}")
        if not path.is_dir():
            raise ValueError(f"STATIC_DIR is not a directory: {v}")
        if not os.access(path, os.R_OK):
            raise ValueError(f"STATIC_DIR is not readable: {v}")
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
