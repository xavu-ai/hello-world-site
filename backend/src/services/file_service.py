"""File service for business logic."""

import hashlib
import shutil
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import AsyncGenerator, Optional

import aiofiles
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.storage import StorageSettings, get_storage_settings
from ..exceptions.file_exceptions import (
    FileNotFoundError,
    FileTooLargeError,
    InvalidFileTypeError,
    StorageError,
)
from ..models.file import File

logger = structlog.get_logger()


class FileService:
    """Service for handling file operations."""

    def __init__(self, session: AsyncSession, storage_settings: Optional[StorageSettings] = None):
        self.session = session
        self.storage_settings = storage_settings or get_storage_settings()
        self.storage_path = self.storage_settings.storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _generate_storage_filename(self, original_name: str) -> str:
        """Generate a unique storage filename."""
        ext = Path(original_name).suffix
        return f"{uuid.uuid4().hex}{ext}"

    def _calculate_checksum(self, content: bytes) -> str:
        """Calculate SHA-256 checksum of file content."""
        return hashlib.sha256(content).hexdigest()

    async def _calculate_checksum_stream(self, file_path: Path) -> str:
        """Calculate checksum by streaming the file."""
        sha256_hash = hashlib.sha256()
        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(8192):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    async def upload_file(
        self,
        content: bytes,
        original_name: str,
        mime_type: str,
        user_id: Optional[uuid.UUID] = None,
        expires_in_hours: Optional[int] = None,
    ) -> File:
        """Upload a file and store its metadata."""
        # Validate file size
        if len(content) > self.storage_settings.max_file_size:
            raise FileTooLargeError(
                f"File size {len(content)} exceeds maximum {self.storage_settings.max_file_size}"
            )

        # Validate file type
        if not self.storage_settings.is_type_allowed(mime_type):
            raise InvalidFileTypeError(f"File type {mime_type} is not allowed")

        # Generate storage path and filename
        filename = self._generate_storage_filename(original_name)
        storage_path = self.storage_path / filename

        # Calculate checksum before saving
        checksum = self._calculate_checksum(content)

        # Save file to storage
        try:
            async with aiofiles.open(storage_path, "wb") as f:
                await f.write(content)
        except Exception as e:
            raise StorageError(f"Failed to save file: {e}")

        # Calculate expiration time
        expires_at = None
        if expires_in_hours is not None:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)

        # Create database record
        file_record = File(
            filename=filename,
            original_name=original_name,
            mime_type=mime_type,
            size_bytes=len(content),
            storage_path=str(storage_path),
            checksum=checksum,
            expires_at=expires_at,
            uploaded_by=user_id,
        )

        self.session.add(file_record)
        await self.session.flush()
        await self.session.refresh(file_record)

        logger.info(
            "file_uploaded",
            file_id=file_record.id,
            filename=filename,
            original_name=original_name,
            size_bytes=len(content),
        )

        return file_record

    async def get_file(self, file_id: uuid.UUID) -> File:
        """Get file metadata by ID."""
        stmt = select(File).where(File.id == file_id)
        result = await self.session.execute(stmt)
        file_record = result.scalar_one_or_none()

        if file_record is None:
            raise FileNotFoundError(f"File not found: {file_id}")

        # Check if file has expired
        if file_record.expires_at and file_record.expires_at < datetime.utcnow():
            raise FileNotFoundError(f"File has expired: {file_id}")

        return file_record

    async def stream_file(self, file_id: uuid.UUID) -> AsyncGenerator[bytes, None]:
        """Stream file content."""
        file_record = await self.get_file(file_id)
        file_path = Path(file_record.storage_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File storage not found: {file_record.filename}")

        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(8192):
                yield chunk

    async def delete_file(self, file_id: uuid.UUID, user_id: Optional[uuid.UUID] = None) -> bool:
        """Delete a file and its metadata."""
        file_record = await self.get_file(file_id)

        # Check ownership if user_id provided (for authorization)
        if user_id is not None and file_record.uploaded_by != user_id:
            # Could raise ForbiddenError here, but keeping simple for now
            return False

        # Delete from storage
        file_path = Path(file_record.storage_path)
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                raise StorageError(f"Failed to delete file from storage: {e}")

        # Delete from database
        await self.session.delete(file_record)
        await self.session.flush()

        logger.info("file_deleted", file_id=file_id)

        return True

    async def list_files(
        self,
        user_id: Optional[uuid.UUID] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[File]:
        """List files with optional user filter."""
        stmt = select(File).order_by(File.created_at.desc()).limit(limit).offset(offset)

        if user_id is not None:
            stmt = stmt.where(File.uploaded_by == user_id)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
