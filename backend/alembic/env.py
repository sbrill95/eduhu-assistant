"""Alembic environment configuration."""

import os
import logging

from alembic import context
from sqlalchemy import create_engine

logger = logging.getLogger("alembic.env")


def get_url() -> str:
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is required")
    # Replace postgresql:// with postgresql+pg8000:// for SQLAlchemy
    # (the project uses asyncpg at runtime, pg8000 is a pure-Python sync driver for Alembic)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+pg8000://", 1)
    return url


def run_migrations_online() -> None:
    """Run migrations against a live database."""
    engine = create_engine(get_url())

    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=None)
        with context.begin_transaction():
            context.run_migrations()

    engine.dispose()


run_migrations_online()
