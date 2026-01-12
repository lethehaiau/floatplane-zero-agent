"""add performance indexes

Revision ID: d7f8a3c2e1b4
Revises: 6eabbfa1a915
Create Date: 2026-01-12 05:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7f8a3c2e1b4'
down_revision = '6eabbfa1a915'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add performance indexes for common query patterns.

    Indexes added:
    - idx_messages_session_created: Optimize fetching messages per session in chronological order
    - idx_files_session_id: Optimize fetching files per session
    - idx_sessions_updated_at: Optimize fetching recent sessions (sorted by activity)
    """
    # Index for messages query: "Get all messages for session, ordered by created_at"
    # Used in: GET /api/chat/sessions/{session_id}/messages
    op.create_index(
        'idx_messages_session_created',
        'messages',
        ['session_id', 'created_at'],
        unique=False
    )

    # Index for files query: "Get all files for session"
    # Used in: GET /api/sessions/{session_id}/files
    op.create_index(
        'idx_files_session_id',
        'files',
        ['session_id'],
        unique=False
    )

    # Index for sessions query: "Get recent sessions, ordered by last activity"
    # Used in: GET /api/sessions (sorted by updated_at DESC)
    op.create_index(
        'idx_sessions_updated_at',
        'sessions',
        [sa.text('updated_at DESC')],
        unique=False,
        postgresql_using='btree'
    )


def downgrade():
    """Remove performance indexes."""
    op.drop_index('idx_sessions_updated_at', table_name='sessions')
    op.drop_index('idx_files_session_id', table_name='files')
    op.drop_index('idx_messages_session_created', table_name='messages')
