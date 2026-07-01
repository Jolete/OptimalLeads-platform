from __future__ import annotations

from collections.abc import Awaitable, Callable

from core_infrastructure.drivers.sqlserver.database_composition import bootstrap_sqlserver_database


DatabaseBootstrap = Callable[[str, str, bool], Awaitable[None]]


def resolve_database_bootstrap(provider: str) -> DatabaseBootstrap:
    if provider == "sqlserver":
        return bootstrap_sqlserver_database

    raise ValueError(f"Unsupported persistence provider: {provider}")
