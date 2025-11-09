"""Helpers for running database migrations from the application."""

from __future__ import annotations

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config

logger = logging.getLogger(__name__)


def _alembic_config() -> Config:
    """Build an Alembic ``Config`` pointing at the project configuration."""

    backend_root = Path(__file__).resolve().parents[2]
    config_path = backend_root / "alembic.ini"

    if not config_path.exists():
        raise RuntimeError(
            "Could not locate alembic.ini. Ensure the backend project layout is intact."
        )

    config = Config(str(config_path))
    # Alembic resolves the script location relative to the ini file, so no
    # additional configuration is required here. The database URL is read from
    # the environment by ``app.database`` which Alembic imports as part of the
    # env setup.
    return config


def run_migrations() -> None:
    """Run the latest Alembic migrations.

    Invoked during application startup to ensure the database schema exists
    before handling requests. Errors are logged and re-raised to make failures
    visible during deployment.
    """

    logger.info("Running database migrations")
    config = _alembic_config()
    try:
        command.upgrade(config, "head")
    except Exception:  # pragma: no cover - defensive logging
        logger.exception("Applying database migrations failed")
        raise
    else:
        logger.info("Database migrations applied successfully")
