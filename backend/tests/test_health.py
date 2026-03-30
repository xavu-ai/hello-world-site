"""Tests for health check endpoint."""
import pytest


@pytest.mark.asyncio
async def test_healthz_returns_200(client):
    """Test that /healthz returns 200 status with correct body."""
    response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_healthz_no_auth_required(client):
    """Test that health endpoint doesn't require authentication."""
    response = await client.get("/healthz")
    assert response.status_code == 200
