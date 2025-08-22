"""Add GIN index for user full-text search

Revision ID: d84c27299aee
Revises: f6cb78da36b1
Create Date: 2025-08-07 12:42:48.240346

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd84c27299aee'
down_revision: Union[str, Sequence[str], None] = 'f6cb78da36b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX user_search_idx ON users USING GIN (to_tsvector('english', name || ' ' || email))"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS user_search_idx")
