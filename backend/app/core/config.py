"""Core configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/ai_builder"
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AI Website Builder API"
<<<<<<< HEAD
=======
    GITHUB_TOKEN: str | None = None
>>>>>>> 755d6f6 (feat: implement GitHub project creation API)


settings = Settings()
