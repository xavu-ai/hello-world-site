"""Integration tests for static file server."""

import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def static_dir(tmp_path: Path, monkeypatch) -> Path:
    """Create temporary static directory with test files."""
    static = tmp_path / "static"
    static.mkdir()

    # Create test files
    (static / "index.html").write_text("<html><body>Hello</body></html>")
    (static / "style.css").write_text("body { color: red; }")
    (static / "app.js").write_text("console.log('hello');")

    # Create subdirectory
    images = static / "images"
    images.mkdir()
    (images / "logo.svg").write_text("<svg></svg>")

    # Patch the static directory setting
    from src.config import get_settings

    class TestSettings:
        host = "0.0.0.0"
        port = 3000
        reload = False
        static_dir = static
        static_url = "/static"
        cors_origins = ["*"]

    monkeypatch.setattr("src.config.get_settings", lambda: TestSettings())

    return static


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_endpoint(self, client: TestClient):
        """Test that health endpoint returns OK."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data


class TestStaticEndpoint:
    """Tests for static file serving."""

    def test_static_endpoint_200(self, client: TestClient, static_dir: Path):
        """Test serving a valid static file."""
        response = client.get("/static/style.css")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/css"
        assert response.text == "body { color: red; }"

    def test_static_endpoint_html(self, client: TestClient, static_dir: Path):
        """Test serving HTML file."""
        response = client.get("/static/index.html")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html"

    def test_static_endpoint_js(self, client: TestClient, static_dir: Path):
        """Test serving JavaScript file."""
        response = client.get("/static/app.js")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/javascript"

    def test_static_endpoint_404(self, client: TestClient, static_dir: Path):
        """Test 404 for missing file."""
        response = client.get("/static/nonexistent.txt")
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "FILE_NOT_FOUND"

    def test_static_endpoint_nested(self, client: TestClient, static_dir: Path):
        """Test serving nested static file."""
        response = client.get("/static/images/logo.svg")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/svg+xml"

    def test_static_endpoint_etag(self, client: TestClient, static_dir: Path):
        """Test that ETag header is present."""
        response = client.get("/static/style.css")
        assert response.status_code == 200
        assert "etag" in response.headers

    def test_static_endpoint_download_param(self, client: TestClient, static_dir: Path):
        """Test download query parameter."""
        response = client.get("/static/style.css?download=1")
        assert response.status_code == 200
        # Check Content-Disposition header for download
        assert "content-disposition" in response.headers


class TestLargeFileStreaming:
    """Tests for large file streaming."""

    def test_large_file_streaming(self, client: TestClient, static_dir: Path):
        """Test that large files are streamed correctly."""
        # Create a larger file (1MB)
        large_file = static_dir / "large.dat"
        large_file.write_bytes(b"x" * (1024 * 1024))

        response = client.get("/static/large.dat")
        assert response.status_code == 200
        assert len(response.content) == 1024 * 1024
