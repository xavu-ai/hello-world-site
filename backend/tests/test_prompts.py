"""Tests for prompt endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_prompt(client: AsyncClient) -> None:
    """Test creating a new prompt."""
    response = await client.post("/api/v1/prompts", json={"content": "Build me a landing page"})
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Build me a landing page"
    assert data["status"] == "pending"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_prompt_validation_error(client: AsyncClient) -> None:
    """Test creating a prompt with empty content fails validation."""
    response = await client.post("/api/v1/prompts", json={"content": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_prompt(client: AsyncClient) -> None:
    """Test getting a prompt by ID."""
    # First create a prompt
    create_response = await client.post(
        "/api/v1/prompts", json={"content": "Create a portfolio website"}
    )
    assert create_response.status_code == 201
    created = create_response.json()
    prompt_id = created["id"]

    # Now get it
    response = await client.get(f"/api/v1/prompts/{prompt_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == prompt_id
    assert data["content"] == "Create a portfolio website"


@pytest.mark.asyncio
async def test_get_prompt_not_found(client: AsyncClient) -> None:
    """Test getting a non-existent prompt returns 404."""
    response = await client.get("/api/v1/prompts/12345678-1234-1234-1234-123456789abc")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_prompts(client: AsyncClient) -> None:
    """Test listing prompts with pagination."""
    # Create a few prompts
    for i in range(3):
        response = await client.post("/api/v1/prompts", json={"content": f"Prompt {i}"})
        assert response.status_code == 201

    # List prompts
    response = await client.get("/api/v1/prompts?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert data["skip"] == 0
    assert data["limit"] == 2


@pytest.mark.asyncio
async def test_list_prompts_pagination(client: AsyncClient) -> None:
    """Test pagination works correctly."""
    # Create prompts
    for i in range(5):
        response = await client.post("/api/v1/prompts", json={"content": f"Prompt {i}"})
        assert response.status_code == 201

    # Get first page
    response = await client.get("/api/v1/prompts?skip=0&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 3

    # Get second page
    response = await client.get("/api/v1/prompts?skip=3&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
