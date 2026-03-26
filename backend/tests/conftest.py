"""Pytest configuration and fixtures."""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add the backend directory to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from src.server import app


@pytest.fixture
def client() -> TestClient:
    """Synchronous test client fixture for static file server."""
    return TestClient(app)
