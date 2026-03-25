"""Unit tests for static file server."""

import hashlib
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.exceptions import FileNotFoundError, PathTraversalError
from src.routers.static import check_path_traversal, generate_etag, get_mime_type


class TestPathTraversal:
    """Tests for path traversal protection."""

    def test_path_traversal_blocked_absolute(self, tmp_path: Path):
        """Test that absolute path traversal is blocked."""
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        malicious_path = tmp_path / ".." / "etc" / "passwd"

        with pytest.raises(PathTraversalError):
            check_path_traversal(malicious_path, static_dir)

    def test_path_traversal_blocked_relative(self, tmp_path: Path):
        """Test that relative path traversal is blocked."""
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        malicious_path = static_dir / ".." / ".." / "etc" / "passwd"

        with pytest.raises(PathTraversalError):
            check_path_traversal(malicious_path, static_dir)

    def test_path_traversal_blocked_encoded(self, tmp_path: Path):
        """Test that encoded path traversal is blocked."""
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        malicious_path = static_dir / "%2e%2e" / "%2e%2e" / "etc" / "passwd"

        with pytest.raises(PathTraversalError):
            check_path_traversal(malicious_path, static_dir)

    def test_valid_file_allowed(self, tmp_path: Path):
        """Test that valid file paths within static dir are allowed."""
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        valid_file = static_dir / "images" / "logo.png"
        valid_file.parent.mkdir()
        valid_file.write_bytes(b"fake image")

        # Should not raise
        check_path_traversal(valid_file, static_dir)


class TestMimeTypes:
    """Tests for MIME type detection."""

    def test_html_mime_type(self):
        """Test HTML MIME type detection."""
        assert get_mime_type(Path("index.html")) == "text/html"
        assert get_mime_type(Path("page.htm")) == "text/html"

    def test_css_mime_type(self):
        """Test CSS MIME type detection."""
        assert get_mime_type(Path("style.css")) == "text/css"

    def test_js_mime_type(self):
        """Test JavaScript MIME type detection."""
        assert get_mime_type(Path("app.js")) == "application/javascript"
        assert get_mime_type(Path("module.mjs")) == "application/javascript"

    def test_image_mime_types(self):
        """Test image MIME type detection."""
        assert get_mime_type(Path("image.png")) == "image/png"
        assert get_mime_type(Path("photo.jpg")) == "image/jpeg"
        assert get_mime_type(Path("photo.jpeg")) == "image/jpeg"
        assert get_mime_type(Path("graphic.svg")) == "image/svg+xml"
        assert get_mime_type(Path("icon.webp")) == "image/webp"

    def test_font_mime_types(self):
        """Test font MIME type detection."""
        assert get_mime_type(Path("font.woff")) == "font/woff"
        assert get_mime_type(Path("font.woff2")) == "font/woff2"
        assert get_mime_type(Path("font.ttf")) == "font/ttf"

    def test_unknown_mime_type(self):
        """Test default MIME type for unknown extensions."""
        assert get_mime_type(Path("file.xyz")) == "application/octet-stream"
        assert get_mime_type(Path("noextension")) == "application/octet-stream"


class TestEtagGeneration:
    """Tests for ETag generation."""

    def test_etag_changes_with_content(self, tmp_path: Path):
        """Test that ETag changes when file content changes."""
        file_path = tmp_path / "test.txt"
        file_path.write_bytes(b"original")
        etag1 = generate_etag(file_path)

        file_path.write_bytes(b"modified")
        etag2 = generate_etag(file_path)

        assert etag1 != etag2

    def test_etag_format(self, tmp_path: Path):
        """Test that ETag is a valid hex string."""
        file_path = tmp_path / "test.txt"
        file_path.write_bytes(b"content")
        etag = generate_etag(file_path)

        # MD5 hash produces 32 character hex string
        assert len(etag) == 32
        assert all(c in "0123456789abcdef" for c in etag)
