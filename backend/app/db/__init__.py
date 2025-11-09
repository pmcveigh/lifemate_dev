"""Database utilities for application lifecycle hooks."""

from app.db.migrations import run_migrations

__all__ = ["run_migrations"]
