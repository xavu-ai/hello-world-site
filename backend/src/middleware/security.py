from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
from src.config import get_settings


def setup_security_middleware(app: FastAPI) -> None:
    settings = get_settings()
    
    # CORS - restrictive for prod
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS if settings.ENV == "production" else ["*"],
        allow_methods=["GET", "HEAD"],
        allow_headers=["*"],
    )

    # Security headers middleware
    @app.middleware("http")
    async def security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
