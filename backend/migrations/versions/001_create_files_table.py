"""Create files table migration.

Revision ID: 001
Revises:
Create Date: 2024-01-15 10:30:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create files table."""
    op.create_table(
        'files',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('original_name', sa.String(255), nullable=False),
        sa.Column('mime_type', sa.String(127), nullable=False),
        sa.Column('size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('storage_path', sa.String(500), nullable=False, unique=True),
        sa.Column('checksum', sa.String(64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='SET NULL'),
        sa.CheckConstraint('size_bytes > 0', name='check_size_bytes_positive'),
    )

    # Create indexes
    op.create_index('idx_files_filename', 'files', ['filename'])
    op.create_index('idx_files_created_at', 'files', ['created_at'])
    op.create_index('idx_files_uploaded_by', 'files', ['uploaded_by'])
    op.create_index('idx_files_expires_at', 'files', ['expires_at'], postgresql_where=sa.text('expires_at IS NOT NULL'))


def downgrade() -> None:
    """Drop files table."""
    op.drop_index('idx_files_expires_at', table_name='files')
    op.drop_index('idx_files_uploaded_by', table_name='files')
    op.drop_index('idx_files_created_at', table_name='files')
    op.drop_index('idx_files_filename', table_name='files')
    op.drop_table('files')
