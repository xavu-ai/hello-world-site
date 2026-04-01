"""API routers aggregation."""
from fastapi import APIRouter

from app.routers.auth import router as auth_router
from app.routers.entries import router as entries_router
from app.routers.timeline import router as timeline_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(entries_router)
api_router.include_router(timeline_router)
