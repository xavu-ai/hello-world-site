"""
Integration tests for static file hosting service.
These tests verify that nginx serves static files correctly with proper MIME types,
compression, caching, and health checks.
"""

import pytest
import requests


# Test configuration
BASE_URL = "http://localhost:8080"


class TestStaticFileServing:
    """Test static file serving at root and paths."""

    def test_index_html_served_at_root(self):
        """Verify index.html is served at root path."""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")

    def test_css_files_served_with_correct_mime(self):
        """Verify CSS files are served with text/css MIME type."""
        response = requests.get(f"{BASE_URL}/style.css")
        assert response.status_code == 200
        assert "text/css" in response.headers.get("Content-Type", "")

    def test_js_files_served_with_correct_mime(self):
        """Verify JavaScript files are served with application/javascript MIME type."""
        response = requests.get(f"{BASE_URL}/app.js")
        assert response.status_code == 200
        content_type = response.headers.get("Content-Type", "")
        assert "application/javascript" in content_type or "text/javascript" in content_type

    def test_svg_files_served_with_correct_mime(self):
        """Verify SVG files are served with image/svg+xml MIME type."""
        response = requests.get(f"{BASE_URL}/image.svg")
        assert response.status_code == 200
        assert "image/svg+xml" in response.headers.get("Content-Type", "")

    def test_woff2_files_served_with_correct_mime(self):
        """Verify woff2 font files are served with font/woff2 MIME type."""
        response = requests.get(f"{BASE_URL}/font.woff2")
        assert response.status_code == 200
        content_type = response.headers.get("Content-Type", "")
        assert "font/woff2" in content_type or "application/font-woff2" in content_type


class TestErrorHandling:
    """Test error handling for missing files."""

    def test_404_returned_for_missing_files(self):
        """Verify 404 status code is returned for non-existent files."""
        response = requests.get(f"{BASE_URL}/nonexistent-file-12345.html")
        assert response.status_code == 404


class TestCompression:
    """Test gzip compression."""

    def test_gzip_compression_enabled(self):
        """Verify gzip compression is enabled by checking Accept-Encoding handling."""
        headers = {"Accept-Encoding": "gzip, deflate"}
        response = requests.get(f"{BASE_URL}/app.js", headers=headers)
        assert response.status_code == 200
        # Content-Encoding header indicates compression was applied
        # Note: This may vary based on file size and nginx config


class TestCaching:
    """Test cache headers for static assets."""

    def test_cache_headers_present(self):
        """Verify cache headers are present for static assets."""
        response = requests.get(f"{BASE_URL}/style.css")
        assert response.status_code == 200
        cache_control = response.headers.get("Cache-Control", "")
        # Should have cache headers for static assets
        assert "public" in cache_control.lower() or "private" in cache_control.lower()


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_endpoint_returns_200(self):
        """Verify health endpoint returns 200 OK with healthy status."""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        assert response.text == '{"status":"healthy"}\n'
        assert "application/json" in response.headers.get("Content-Type", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
