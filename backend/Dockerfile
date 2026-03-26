# Multi-stage build for static file server

# Stage 1: Build
FROM python:3.11-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production
FROM python:3.11-slim

# Create non-root user with specific UID
RUN groupadd -r appuser && useradd -r -u 1000 -g appuser appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser src/ ./src/

# Copy static files
COPY --chown=appuser:appuser static/ ./static/

# Copy environment example
COPY --chown=appuser:appuser .env.example ./

USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]
