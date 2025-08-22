"""add task model

Revision ID: a4ff4a5480de
Revises: 03d365621553
Create Date: 2025-08-18 11:53:24.490319
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4ff4a5480de'
down_revision: Union[str, Sequence[str], None] = '03d365621553'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('head', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('assigned_to', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('reporter', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # GIN trigram index on head
    op.create_index(
        "idx_tasks_head_trgm",
        "tasks",
        ["head"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"head": "gin_trgm_ops"},
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_tasks_head_trgm', table_name='tasks', postgresql_using='gin')
    op.drop_table('tasks')
