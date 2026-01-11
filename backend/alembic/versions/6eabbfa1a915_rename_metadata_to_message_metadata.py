"""rename metadata to message_metadata

Revision ID: 6eabbfa1a915
Revises: c1cfd924f4bc
Create Date: 2026-01-10 15:46:31.354783

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6eabbfa1a915'
down_revision: Union[str, None] = 'c1cfd924f4bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename metadata column to message_metadata
    op.alter_column('messages', 'metadata', new_column_name='message_metadata')


def downgrade() -> None:
    # Rename back to metadata
    op.alter_column('messages', 'message_metadata', new_column_name='metadata')
