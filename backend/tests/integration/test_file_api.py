"""Integration tests for file API."""

import uuid
from io import BytesIO

import pytest
from httpx import AsyncClient

from src.server import app


class TestFileUploadDownloadFlow:
    """Integration tests for upload and download flow."""

    @pytest.mark.asyncio
    async def test_upload_and_download_flow(self):
        """Test complete upload and download flow."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Upload a file
            file_content = b"Integration test content"
            files = {"file": ("integration_test.txt", BytesIO(file_content), "text/plain")}

            upload_response = await client.post("/api/v1/files/upload", files=files)
            assert upload_response.status_code == 201

            file_id = upload_response.json()["id"]

            # Download the file
            download_response = await client.get(f"/api/v1/files/{file_id}/download")
            assert download_response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_metadata_after_upload(self):
        """Test getting metadata for an uploaded file."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Upload a file
            file_content = b"Metadata test content"
            files = {"file": ("metadata_test.txt", BytesIO(file_content), "text/plain")}

            upload_response = await client.post("/api/v1/files/upload", files=files)
            assert upload_response.status_code == 201

            file_id = upload_response.json()["id"]

            # Get metadata
            metadata_response = await client.get(f"/api/v1/files/{file_id}")
            assert metadata_response.status_code == 200

            data = metadata_response.json()
            assert data["id"] == file_id
            assert data["original_name"] == "metadata_test.txt"


class TestFileExpiration:
    """Tests for file expiration functionality."""

    @pytest.mark.asyncio
    async def test_upload_with_expiration(self):
        """Test uploading a file with expiration time."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            file_content = b"Expiring content"
            files = {"file": ("expiring.txt", BytesIO(file_content), "text/plain")}
            data = {"expires_in": 1}  # 1 hour

            response = await client.post("/api/v1/files/upload", files=files, data=data)
            assert response.status_code == 201


class TestFileNotFound:
    """Tests for file not found scenarios."""

    @pytest.mark.asyncio
    async def test_download_nonexistent_file(self):
        """Test downloading a file that doesn't exist."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            fake_id = uuid.uuid4()
            response = await client.get(f"/api/v1/files/{fake_id}/download")
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_metadata_nonexistent_file(self):
        """Test getting metadata for a file that doesn't exist."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            fake_id = uuid.uuid4()
            response = await client.get(f"/api/v1/files/{fake_id}")
            assert response.status_code == 404


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            assert response.json() == {"status": "healthy"}
