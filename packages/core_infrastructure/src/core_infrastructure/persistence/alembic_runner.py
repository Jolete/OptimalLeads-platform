from __future__ import annotations

from alembic import command
from alembic.config import Config

from core_infrastructure.persistence.migration_factory import register_migration_runner


def run_alembic_migrations(script_location: str, database_url: str) -> None:
    config = Config()
    config.set_main_option("script_location", script_location)
    config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(config, "head")


register_migration_runner("alembic", lambda: run_alembic_migrations)