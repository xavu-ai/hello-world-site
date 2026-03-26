"""Tests for static file hosting service."""
import hashlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestStaticFileServing:
    """Test static file serving functionality."""

    def test_index_html(self):
        """Verify index.html is served at root."""
        response = client.get("/")
        assert response.status_code == 200, "index.html should be served at root"
        assert "text/html" in response.headers["content-type"]
        assert "Hello World" in response.text

    def test_static_css(self):
        """Verify CSS files are served correctly."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200, "style.css should be found and served"
        assert "text/css" in response.headers["content-type"]

    def test_static_js(self):
        """Verify JS files are served correctly."""
        response = client.get("/static/js/main.js")
        assert response.status_code == 200, "main.js should be found and served"
        assert "application/javascript" in response.headers["content-type"]

    def test_static_nonexistent(self):
        """Verify 404 for non-existent files."""
        response = client.get("/static/nonexistent.file")
        assert response.status_code == 404


class TestPathTraversalProtection:
    """Test path traversal protection."""

    def test_path_traversal_blocked(self):
        """Verify path traversal attacks are blocked."""
        response = client.get("/static/%2e%2e/main.py")
        assert response.status_code == 403

    def test_absolute_path_blocked(self):
        """Verify absolute paths are blocked."""
        response = client.get("/static//etc/passwd")
        assert response.status_code == 403

    def test_parent_directory_blocked(self):
        """Verify parent directory traversal is blocked or returns 404."""
        # FastAPI normalizes paths, so /static/../main.py becomes /static/main.py
        # which returns 404 if not found - this is acceptable
        response = client.get("/static/../main.py")
        assert response.status_code in [403, 404]


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self):
        """Verify health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestETagGeneration:
    """Test ETag generation with SHA-256."""

    def test_etag_header_present(self):
        """Verify ETag header is present for static files."""
        response = client.get("/")
        assert response.status_code == 200
        assert "etag" in response.headers

    def test_etag_format(self):
        """Verify ETag is properly formatted with SHA-256 hash."""
        response = client.get("/")
        assert response.status_code == 200
        etag = response.headers.get("etag", "")
        assert etag.startswith('"') and etag.endswith('"')
        # SHA-256 produces 64 character hex string
        inner = etag[1:-1]
        assert len(inner) == 64
        assert all(c in "0123456789abcdef" for c in inner)

    def test_cache_control_header(self):
        """Verify Cache-Control header is present."""
        response = client.get("/")
        assert response.status_code == 200
        assert "cache-control" in response.headers

    def test_not_modified_response(self):
        """Verify 304 response when ETag matches."""
        # First request to get ETag
        response1 = client.get("/")
        assert response1.status_code == 200
        etag = response1.headers.get("etag")
        assert etag is not None

        # Second request with If-None-Match
        response2 = client.get("/", headers={"If-None-Match": etag})
        assert response2.status_code == 304


class TestMimeTypes:
    """Test MIME type detection."""

    def test_html_mime_type(self):
        """Verify HTML files return text/html."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_css_mime_type(self):
        """Verify CSS files return text/css."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert "text/css" in response.headers.get("content-type", "")

    def test_js_mime_type(self):
        """Verify JS files return application/javascript."""
        response = client.get("/static/js/main.js")
        assert response.status_code == 200
        assert "application/javascript" in response.headers.get("content-type", "")


class TestGzipCompression:
    """Test GZip compression."""

    def test_accepts_gzip(self):
        """Verify server accepts gzip encoding."""
        response = client.get("/", headers={"Accept-Encoding": "gzip"})
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling."""

    def test_404_for_missing_file(self):
        """Verify proper 404 response for missing files."""
        response = client.get("/static/thisdoesnotexist12345.html")
        assert response.status_code == 404

    def test_error_response_format(self):
        """Verify error responses have proper format."""
        response = client.get("/static/doesnotexist.html")
        assert response.status_code == 404
        assert response.headers.get("content-type", "").startswith("application/json")


class TestSecurityHeaders:
    """Test security headers."""

    def test_x_content_type_options(self):
        """Verify X-Content-Type-Options header is present."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.headers.get("x-content-type-options") == "nosniff"

    def test_x_frame_options(self):
        """Verify X-Frame-Options header is present."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.headers.get("x-frame-options") == "DENY"
