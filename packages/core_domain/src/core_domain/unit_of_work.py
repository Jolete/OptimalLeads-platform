from __future__ import annotations

from typing import Protocol, TypeVar

RepositoryType = TypeVar("RepositoryType")


class UnitOfWork(Protocol):
    repositories: dict[str, object]

    async def __aenter__(self) -> "UnitOfWork":
        ...

    async def __aexit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: object | None) -> None:
        ...

    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...

    def get_repository(self, name: str) -> RepositoryType:
        ...
