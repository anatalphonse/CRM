"""add gin index to lead_list

Revision ID: 9e02e39655ec
Revises: d0c8220bd9aa
Create Date: 2025-08-08 22:44:28.517454

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e02e39655ec'
down_revision: Union[str, Sequence[str], None] = 'd0c8220bd9aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        CREATE INDEX IF NOT EXISTS lead_search_idx
        ON leads
        USING GIN (
            to_tsvector(
                'english',
                coalesce(name, '') || ' ' ||
                coalesce(notes, '')
            )
        )
    """)

def downgrade():
    op.execute("DROP INDEX IF EXISTS contact_search_idx")
