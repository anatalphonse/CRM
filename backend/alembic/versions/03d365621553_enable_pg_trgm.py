"""enable pg_trgm

Revision ID: 03d365621553
Revises: 9e02e39655ec
Create Date: 2025-08-09 15:01:44.509985

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '03d365621553'
down_revision: Union[str, Sequence[str], None] = '9e02e39655ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

def downgrade():
    op.execute("DROP EXTENSION IF EXISTS pg_trgm;")