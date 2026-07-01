from __future__ import annotations

import asyncio

from core_infrastructure.drivers.sqlserver.database_bootstrap import drop_database_if_exists, ensure_database_exists
from core_infrastructure.persistence.alembic_runner import run_alembic_migrations
from core_infrastructure.persistence.persistence_factory import register_database_bootstrap


async def bootstrap_sqlserver_database(database_url: str, alembic_path: str, reset_database: bool) -> None:
    if reset_database:
        await drop_database_if_exists(database_url)
    await ensure_database_exists(database_url)
    await asyncio.to_thread(run_alembic_migrations, alembic_path, database_url)


register_database_bootstrap("sqlserver", lambda: bootstrap_sqlserver_database)
