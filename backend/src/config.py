from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    ENV: str = "development"
    STATIC_DIR: str = "static"
    ALLOWED_HOSTS: List[str] = ["*"]
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
