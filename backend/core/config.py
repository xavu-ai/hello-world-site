from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "AI Website Builder API"
    debug: bool = False
    redis_url: str | None = None
    max_prompt_length: int = 2000

    class Config:
        env_prefix = "APP_"
        env_file = ".env"


settings = Settings()
