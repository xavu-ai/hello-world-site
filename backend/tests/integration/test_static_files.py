"""Integration tests for static file serving."""

import pytest
from fastapi.testclient import TestClient


def test_index_html_served_with_correct_mime(client: TestClient):
    """Test that index.html is served with text/html content type."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert b"<!DOCTYPE html>" in response.content or b"<html" in response.content


def test_css_file_loads_without_404(client: TestClient):
    """Test that CSS file loads successfully."""
    response = client.get("/css/style.css")

    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]


def test_js_file_loads_without_404(client: TestClient):
    """Test that JavaScript file loads successfully."""
    response = client.get("/js/script.js")

    assert response.status_code == 200
    assert "application/javascript" in response.headers["content-type"]


def test_404_for_missing_file(client: TestClient):
    """Test that missing files return 404."""
    response = client.get("/nonexistent.html")

    assert response.status_code == 404
    assert response.json()["error"] == "FILE_NOT_FOUND"


def test_404_for_missing_css(client: TestClient):
    """Test that missing CSS file returns 404."""
    response = client.get("/css/nonexistent.css")

    assert response.status_code == 404


def test_404_for_missing_js(client: TestClient):
    """Test that missing JS file returns 404."""
    response = client.get("/js/nonexistent.js")

    assert response.status_code == 404


def test_caching_headers_present(client: TestClient):
    """Test that ETag header is present for static files."""
    response = client.get("/css/style.css")

    assert response.status_code == 200
    assert "ETag" in response.headers


def test_index_html_content(client: TestClient):
    """Test that index.html contains expected content."""
    response = client.get("/")

    assert response.status_code == 200
    content = response.text
    assert "Hello, World!" in content
    assert 'href="/css/style.css"' in content
    assert 'src="/js/script.js"' in content


def test_css_content(client: TestClient):
    """Test that CSS file contains expected styles."""
    response = client.get("/css/style.css")

    assert response.status_code == 200
    content = response.text
    assert "font-family" in content
    assert "body" in content


def test_js_content(client: TestClient):
    """Test that JS file contains expected code."""
    response = client.get("/js/script.js")

    assert response.status_code == 200
    content = response.text
    assert "greet()" in content or "console.log" in content
