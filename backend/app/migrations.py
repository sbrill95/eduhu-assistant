"""Run Alembic migrations programmatically at startup."""

import logging
import os

from alembic import command
from alembic.config import Config

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    """Run 'alembic upgrade head'. Call before init_pool()."""
    logger.info("Running database migrations...")

    # Build Alembic config programmatically
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ini_path = os.path.join(base_dir, "alembic.ini")

    cfg = Config(ini_path)
    cfg.set_main_option("script_location", os.path.join(base_dir, "alembic"))
    cfg.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

    command.upgrade(cfg, "head")
    logger.info("Database migrations complete.")
