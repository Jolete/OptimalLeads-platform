from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypeAlias


DatabaseBootstrap = Callable[[str, str, bool], Awaitable[None]]
DatabaseBootstrapFactory: TypeAlias = Callable[[], DatabaseBootstrap]
MigrationRunnerFactory: TypeAlias = Callable[[], Callable[[str, str], None]]


_DATABASE_BOOTSTRAPS: dict[str, DatabaseBootstrapFactory] = {}
_MIGRATION_RUNNERS: dict[str, MigrationRunnerFactory] = {}


def register_database_bootstrap(provider: str, factory: DatabaseBootstrapFactory) -> None:
    _DATABASE_BOOTSTRAPS[provider] = factory


def register_migration_runner(provider: str, factory: MigrationRunnerFactory) -> None:
    _MIGRATION_RUNNERS[provider] = factory


def create_database_bootstrap(provider: str) -> DatabaseBootstrap:
    try:
        factory = _DATABASE_BOOTSTRAPS[provider]
    except KeyError as exc:
        raise ValueError(f"Unsupported persistence provider: {provider}") from exc

    return factory()


def create_migration_runner(provider: str) -> Callable[[str, str], None]:
    try:
        factory = _MIGRATION_RUNNERS[provider]
    except KeyError as exc:
        raise ValueError(f"Unsupported migration provider: {provider}") from exc

    return factory()
