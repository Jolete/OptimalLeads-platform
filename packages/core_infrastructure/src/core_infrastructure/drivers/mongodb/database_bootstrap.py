from __future__ import annotations


async def bootstrap_mongodb_database(database_url: str, alembic_path: str, reset_database: bool) -> None:
    _ = database_url, alembic_path, reset_database
    return None
