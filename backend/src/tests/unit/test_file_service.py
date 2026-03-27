"""Unit tests for file service."""

import hashlib
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.exceptions.file_exceptions import (
    FileNotFoundError,
    FileTooLargeError,
    InvalidFileTypeError,
    StorageError,
)
from src.services.file_service import FileService


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def mock_storage_settings():
    """Create mock storage settings."""
    settings = MagicMock()
    settings.storage_path = Path("/tmp/test_storage")
    settings.max_file_size = 104857600  # 100MB
    settings.allowed_mime_types = ["image/*", "application/pdf", "text/*"]
    settings.is_type_allowed = lambda mt: mt.startswith("image/") or mt == "application/pdf" or mt.startswith("text/")
    return settings


@pytest.fixture
def file_service(mock_session, mock_storage_settings):
    """Create a file service with mocked dependencies."""
    return FileService(mock_session, mock_storage_settings)


class TestFileServiceUpload:
    """Tests for file upload functionality."""

    @pytest.mark.asyncio
    async def test_upload_file_creates_record(self, file_service, mock_session):
        """Test that upload_file creates a database record."""
        content = b"test file content"
        original_name = "test.txt"
        mime_type = "text/plain"

        # Mock the session refresh to set attributes
        async def mock_refresh(record):
            record.id = uuid.uuid4()
            record.created_at = datetime.utcnow()

        mock_session.refresh = mock_refresh

        result = await file_service.upload_file(
            content=content,
            original_name=original_name,
            mime_type=mime_type,
        )

        mock_session.add.assert_called_once()
        mock_session.flush.assert_called()

    @pytest.mark.asyncio
    async def test_upload_file_raises_when_too_large(self, file_service):
        """Test that upload_file raises FileTooLargeError for oversized files."""
        content = b"x" * (file_service.storage_settings.max_file_size + 1)

        with pytest.raises(FileTooLargeError):
            await file_service.upload_file(
                content=content,
                original_name="large.txt",
                mime_type="text/plain",
            )

    @pytest.mark.asyncio
    async def test_upload_file_raises_when_type_not_allowed(self, file_service):
        """Test that upload_file raises InvalidFileTypeError for disallowed types."""
        content = b"malicious content"

        with pytest.raises(InvalidFileTypeError):
            await file_service.upload_file(
                content=content,
                original_name="malware.exe",
                mime_type="application/x-executable",
            )

    @pytest.mark.asyncio
    async def test_upload_file_calculates_checksum(self, file_service, mock_session):
        """Test that upload_file calculates SHA-256 checksum."""
        content = b"test content for checksum"
        expected_checksum = hashlib.sha256(content).hexdigest()

        async def mock_refresh(record):
            record.id = uuid.uuid4()
            record.created_at = datetime.utcnow()

        mock_session.refresh = mock_refresh

        result = await file_service.upload_file(
            content=content,
            original_name="test.txt",
            mime_type="text/plain",
        )

        assert result.checksum == expected_checksum


class TestFileServiceGet:
    """Tests for file retrieval functionality."""

    @pytest.mark.asyncio
    async def test_get_file_raises_when_not_found(self, file_service, mock_session):
        """Test that get_file raises FileNotFoundError when file doesn't exist."""
        mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=lambda: None))

        with pytest.raises(FileNotFoundError):
            await file_service.get_file(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_get_file_raises_when_expired(self, file_service, mock_session):
        """Test that get_file raises FileNotFoundError for expired files."""
        expired_file = MagicMock()
        expired_file.expires_at = datetime.utcnow() - timedelta(hours=1)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = expired_file
        mock_session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(FileNotFoundError):
            await file_service.get_file(uuid.uuid4())


class TestFileServiceDelete:
    """Tests for file deletion functionality."""

    @pytest.mark.asyncio
    async def test_delete_file_removes_from_storage(self, file_service, mock_session, tmp_path):
        """Test that delete_file removes the file from storage."""
        # Create a temp file to delete
        test_file = tmp_path / "test_file.txt"
        test_file.write_bytes(b"test content")

        file_record = MagicMock()
        file_record.id = uuid.uuid4()
        file_record.storage_path = str(test_file)
        file_record.uploaded_by = None
        file_record.expires_at = None

        # First call returns file metadata, second call for refresh after add
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = file_record
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await file_service.delete_file(file_record.id)

        assert result is True
        mock_session.delete.assert_called_once()


class TestFileServiceChecksum:
    """Tests for checksum calculation."""

    def test_calculate_checksum(self, file_service):
        """Test checksum calculation for bytes."""
        content = b"hello world"
        expected = hashlib.sha256(content).hexdigest()

        result = file_service._calculate_checksum(content)

        assert result == expected

    @pytest.mark.asyncio
    async def test_calculate_checksum_stream(self, file_service, tmp_path):
        """Test checksum calculation via streaming."""
        test_file = tmp_path / "checksum_test.txt"
        content = b"streamed content for checksum"
        test_file.write_bytes(content)

        expected = hashlib.sha256(content).hexdigest()

        result = await file_service._calculate_checksum_stream(test_file)

        assert result == expected
