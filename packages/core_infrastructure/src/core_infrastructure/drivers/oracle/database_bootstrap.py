from __future__ import annotations

from core_infrastructure.drivers.sqlserver.database_bootstrap import drop_database_if_exists, ensure_database_exists


async def bootstrap_oracle_database(database_url: str, alembic_path: str, reset_database: bool) -> None:
    if reset_database:
        await drop_database_if_exists(database_url)
    await ensure_database_exists(database_url)
