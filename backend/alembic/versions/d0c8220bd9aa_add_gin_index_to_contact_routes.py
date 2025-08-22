"""add gin index to contact routes

Revision ID: d0c8220bd9aa
Revises: 6ee7282734ee
Create Date: 2025-08-08 13:02:36.471530

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0c8220bd9aa'
down_revision: Union[str, Sequence[str], None] = '6ee7282734ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        CREATE INDEX IF NOT EXISTS contact_search_idx
        ON contacts
        USING GIN (
            to_tsvector(
                'english',
                coalesce(name, '') || ' ' ||
                coalesce(email, '') || ' ' ||
                coalesce(phone, '') || ' ' ||
                coalesce(company, '') || ' ' ||
                coalesce(notes, '')
            )
        )
    """)

def downgrade():
    op.execute("DROP INDEX IF EXISTS contact_search_idx")
