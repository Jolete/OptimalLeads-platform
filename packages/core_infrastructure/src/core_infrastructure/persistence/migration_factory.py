from __future__ import annotations

from collections.abc import Callable


MigrationRunner = Callable[[str, str], None]
MigrationRunnerFactory = Callable[[], MigrationRunner]


_MIGRATION_RUNNERS: dict[str, MigrationRunnerFactory] = {}


def register_migration_runner(provider: str, factory: MigrationRunnerFactory) -> None:
    _MIGRATION_RUNNERS[provider] = factory


def create_migration_runner(provider: str) -> MigrationRunner:
    try:
        factory = _MIGRATION_RUNNERS[provider]
    except KeyError as exc:
        raise ValueError(f"Unsupported migration provider: {provider}") from exc

    return factory()
