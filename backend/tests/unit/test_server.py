"""Unit tests for server module."""

import pytest
from fastapi.testclient import TestClient


def test_security_headers_present(client: TestClient):
    """Test that security headers are present in responses."""
    response = client.get("/health")

    assert response.status_code == 200
    assert "Content-Security-Policy" in response.headers
    assert "Strict-Transport-Security" in response.headers
    assert "X-Frame-Options" in response.headers
    assert "X-Content-Type-Options" in response.headers
    assert "Referrer-Policy" in response.headers
    assert "Permissions-Policy" in response.headers


def test_csp_header_value(client: TestClient):
    """Test Content-Security-Policy header has expected directives."""
    response = client.get("/health")

    csp = response.headers["Content-Security-Policy"]
    assert "default-src 'self'" in csp
    assert "script-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp


def test_hsts_header(client: TestClient):
    """Test Strict-Transport-Security header."""
    response = client.get("/health")

    hsts = response.headers["Strict-Transport-Security"]
    assert "max-age=31536000" in hsts
    assert "includeSubDomains" in hsts


def test_x_frame_options(client: TestClient):
    """Test X-Frame-Options is DENY."""
    response = client.get("/health")

    assert response.headers["X-Frame-Options"] == "DENY"


def test_x_content_type_options(client: TestClient):
    """Test X-Content-Type-Options is nosniff."""
    response = client.get("/health")

    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_health_endpoint_returns_200(client: TestClient):
    """Test health endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
