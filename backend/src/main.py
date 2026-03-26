import logging
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.config import get_settings
from src.exceptions import StaticFileError
from src.middleware.security import setup_security_middleware
from src.middleware.logging import setup_logging_middleware
from src.routers.static import router as static_router

# Configure logging
logging.basicConfig(
    level=get_settings().LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="Static File Hosting",
    description="FastAPI static file hosting service",
    version="1.0.0"
)

# Setup middleware
setup_security_middleware(app)
setup_logging_middleware(app)

# Include routers
app.include_router(static_router)


# Exception handlers
@app.exception_handler(StaticFileError)
async def static_file_exception_handler(request: Request, exc: StaticFileError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
