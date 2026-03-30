"""API routers aggregation."""
from fastapi import APIRouter

from app.routers.timeline import router as timeline_router

api_router = APIRouter()
api_router.include_router(timeline_router)
