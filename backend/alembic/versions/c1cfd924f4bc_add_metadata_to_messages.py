"""add metadata to messages

Revision ID: c1cfd924f4bc
Revises: 4a2b8c1f3e5d
Create Date: 2026-01-10 15:42:34.736725

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'c1cfd924f4bc'
down_revision: Union[str, None] = '4a2b8c1f3e5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add metadata JSONB column to messages table
    op.add_column('messages', sa.Column('metadata', JSONB, nullable=True))


def downgrade() -> None:
    # Remove metadata column from messages table
    op.drop_column('messages', 'metadata')
