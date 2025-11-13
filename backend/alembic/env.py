from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.core.database import Base
from app.models import user, contact, leads, task  # import all models

# Alembic Config
config = context.config

# Replace async URL (asyncpg) with sync URL (psycopg2)
sync_url = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
config.set_main_option("sqlalchemy.url", sync_url)

# Logging
if config.config_file_name:
    fileConfig(config.config_file_name)

# Metadata
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in offline mode."""
    context.configure(
        url=sync_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in online mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
