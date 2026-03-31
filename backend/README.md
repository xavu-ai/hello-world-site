# Static File Hosting

FastAPI-based static file hosting service with security middleware and SPA fallback support.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn src.main:app --reload

# Or run directly
python -m src.main
```

## Endpoints

- `GET /` - Serve index.html
- `GET /{path}` - Serve static files with SPA fallback
- `GET /health` - Health check

## Configuration

Environment variables:
- `ENV` - Environment (development/production), default: development
- `STATIC_DIR` - Static files directory, default: static
- `ALLOWED_HOSTS` - Allowed hosts list
- `LOG_LEVEL` - Logging level, default: INFO

## Docker

```bash
# Build and run
docker-compose up -d

# Or build manually
docker build -t static-server ./backend
docker run -p 8000:8000 static-server
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run only unit tests
pytest tests/unit

# Run only integration tests
pytest tests/integration
```
