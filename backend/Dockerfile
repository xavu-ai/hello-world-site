# Builder stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install uv
RUN pip install uv

# Copy source and dependencies
COPY pyproject.toml ./
COPY src/ ./src/

# Sync dependencies
RUN uv sync --frozen --no-dev

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser

USER 1000

EXPOSE 6100

CMD ["uv", "run", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "6100"]
