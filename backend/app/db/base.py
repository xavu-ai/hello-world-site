"""Database base with all models."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


# Import all models to register them with Base.metadata
from app.models.github_project import GitHubProject  # noqa: E402, F401
from app.models.prompt import Prompt  # noqa: E402, F401
