"""API router aggregator."""
from fastapi import APIRouter

from app.api.v1 import github_projects, prompts

api_router = APIRouter()
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
api_router.include_router(
    github_projects.router, prefix="/github/projects", tags=["github-projects"]
)
