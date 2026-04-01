"""Tests for auth endpoints."""
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.models.auth import Contributor


class TestAuthSchemas:
    """Test auth schema validation."""

    def test_register_request_valid(self):
        """Test valid registration request schema."""
        from app.schemas.auth import RegisterRequest
        
        request = RegisterRequest(email="test@example.com", password="password123")
        assert request.email == "test@example.com"
        assert request.password == "password123"

    def test_register_request_password_too_short(self):
        """Test registration fails with short password."""
        from pydantic import ValidationError
        from app.schemas.auth import RegisterRequest
        
        with pytest.raises(ValidationError):
            RegisterRequest(email="test@example.com", password="short")

    def test_register_request_invalid_email(self):
        """Test registration fails with invalid email."""
        from pydantic import ValidationError
        from app.schemas.auth import RegisterRequest
        
        with pytest.raises(ValidationError):
            RegisterRequest(email="not-an-email", password="password123")

    def test_login_request_valid(self):
        """Test valid login request schema."""
        from app.schemas.auth import LoginRequest
        
        request = LoginRequest(email="test@example.com", password="password123")
        assert request.email == "test@example.com"
        assert request.password == "password123"


class TestAuthEndpoints:
    """Test auth endpoints."""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Test successful registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "newuser@example.com", "password": "password123"},
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == "newuser@example.com"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, db_session):
        """Test registration fails with duplicate email."""
        from app.models.auth import Contributor
        from app.routers.auth import hash_password
        
        existing = Contributor(
            id=uuid4(),
            email="existing@example.com",
            hashed_password=hash_password("password123"),
        )
        db_session.add(existing)
        await db_session.commit()
        
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "existing@example.com", "password": "password123"},
        )
        assert response.status_code == 409
        assert response.json()["detail"]["message"] == "Email already registered"

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration fails with invalid email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "not-an-email", "password": "password123"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, db_session):
        """Test successful login."""
        from app.models.auth import Contributor
        from app.routers.auth import hash_password
        
        user = Contributor(
            id=uuid4(),
            email="loginuser@example.com",
            hashed_password=hash_password("password123"),
        )
        db_session.add(user)
        await db_session.commit()
        
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "loginuser@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["expires_in"] == 86400

    @pytest.mark.asyncio
    async def test_login_invalid_email(self, client: AsyncClient):
        """Test login fails with non-existent email."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"},
        )
        assert response.status_code == 401
        assert response.json()["detail"]["message"] == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client: AsyncClient, db_session):
        """Test login fails with wrong password."""
        from app.models.auth import Contributor
        from app.routers.auth import hash_password
        
        user = Contributor(
            id=uuid4(),
            email="wrongpw@example.com",
            hashed_password=hash_password("correctpassword"),
        )
        db_session.add(user)
        await db_session.commit()
        
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "wrongpw@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert response.json()["detail"]["message"] == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_logout_success(self, client: AsyncClient, db_session):
        """Test successful logout with valid token."""
        from app.models.auth import Contributor
        from app.routers.auth import hash_password
        
        user = Contributor(
            id=uuid4(),
            email="logoutuser@example.com",
            hashed_password=hash_password("password123"),
        )
        db_session.add(user)
        await db_session.commit()
        
        # First login to get a valid token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "logoutuser@example.com", "password": "password123"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["token"]
        
        # Then logout with the valid token
        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out"

    @pytest.mark.asyncio
    async def test_logout_no_auth(self, client: AsyncClient):
        """Test logout fails without authentication."""
        response = await client.post("/api/v1/auth/logout")
        assert response.status_code == 401
