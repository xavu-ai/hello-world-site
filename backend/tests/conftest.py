"""Pytest configuration and fixtures."""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def setup_test_settings(tmp_path_factory):
    """Set up test static directory before any imports happen."""
    # Create a session-scoped temp directory
    test_static = tmp_path_factory.mktemp("static")

    # Create test files
    (test_static / "index.html").write_text("<h1>Hello World</h1>")
    css_dir = test_static / "css"
    css_dir.mkdir()
    (css_dir / "style.css").write_text("body { color: red; }")
    js_dir = test_static / "js"
    js_dir.mkdir()
    (js_dir / "main.js").write_text("console.log('test');")

    # Set environment variable BEFORE any imports
    os.environ["STATIC_DIR"] = str(test_static)

    # Clear settings cache if it exists
    try:
        from settings import get_settings
        get_settings.cache_clear()
    except Exception:
        pass

    yield str(test_static)

    # Cleanup
    if "STATIC_DIR" in os.environ:
        del os.environ["STATIC_DIR"]


@pytest.fixture
def client() -> TestClient:
    """Synchronous test client fixture for static file server."""
    from main import app
    return TestClient(app)
