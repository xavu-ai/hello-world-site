"""Application configuration using pydantic-settings."""
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/openclaw"
    SECRET_KEY: str = "change-me"
    CORS_ORIGINS: str = "http://localhost:8100"

    @field_validator("CORS_ORIGINS")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse CORS_ORIGINS from comma-separated string to list."""
        return [origin.strip() for origin in v.split(",") if origin.strip()]

    def validate_required(self) -> None:
        """Validate that required configuration is present."""
        if self.SECRET_KEY == "change-me":
            raise ValueError("SECRET_KEY must be set to a secure value")


settings = Settings()
