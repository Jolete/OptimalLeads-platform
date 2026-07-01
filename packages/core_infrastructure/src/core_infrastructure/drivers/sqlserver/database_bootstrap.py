from __future__ import annotations

from urllib.parse import quote_plus, urlparse

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


def _database_name_from_url(database_url: str) -> str:
    parsed = urlparse(database_url)
    if parsed.scheme not in {"mssql", "mssql+aioodbc"}:
        raise ValueError(f"SQL Server bootstrap only supports mssql URLs, got {parsed.scheme!r}")
    return parsed.path.lstrip("/")


def _server_url_from_database_url(database_url: str) -> str:
    parsed = urlparse(database_url)
    if parsed.scheme not in {"mssql", "mssql+aioodbc"}:
        raise ValueError(f"SQL Server bootstrap only supports mssql URLs, got {parsed.scheme!r}")
    driver = parsed.query.split("driver=")[-1].split("&", 1)[0] if "driver=" in parsed.query else "ODBC Driver 17 for SQL Server"
    username = parsed.username or ""
    password = parsed.password or ""
    host = parsed.hostname or "localhost"
    port = f":{parsed.port}" if parsed.port else ""
    auth = f"{quote_plus(username)}:{quote_plus(password)}@" if username else ""
    return f"mssql+aioodbc://{auth}{host}{port}/master?driver={driver}&TrustServerCertificate=yes"


async def ensure_database_exists(database_url: str) -> None:
    database_name = _database_name_from_url(database_url)
    server_url = _server_url_from_database_url(database_url)
    engine = create_async_engine(server_url, future=True)
    try:
        async with engine.connect() as connection:
            await connection.execution_options(isolation_level="AUTOCOMMIT")
            await connection.execute(
                text(
                    "DECLARE @sql nvarchar(max) = N'IF DB_ID(''' + :database_name + N''') IS NULL CREATE DATABASE ' + QUOTENAME(:database_name); EXEC(@sql)"
                ),
                {"database_name": database_name},
            )
    finally:
        await engine.dispose()


async def drop_database_if_exists(database_url: str) -> None:
    database_name = _database_name_from_url(database_url)
    server_url = _server_url_from_database_url(database_url)
    engine = create_async_engine(server_url, future=True)
    try:
        async with engine.connect() as connection:
            await connection.execution_options(isolation_level="AUTOCOMMIT")
            await connection.execute(
                text(
                    "DECLARE @sql nvarchar(max) = N'IF DB_ID(''' + :database_name + N''') IS NOT NULL BEGIN ALTER DATABASE ' + QUOTENAME(:database_name) + N' SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE ' + QUOTENAME(:database_name) + N'; END'; EXEC(@sql)"
                ),
                {"database_name": database_name},
            )
    finally:
        await engine.dispose()