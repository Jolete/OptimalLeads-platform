from __future__ import annotations

from collections.abc import Callable
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core_domain import UnitOfWork


RepositoryFactory = Callable[[AsyncSession], object]


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession], repository_factories: dict[str, RepositoryFactory]) -> None:
        self._session_factory = session_factory
        self._repository_factories = repository_factories
        self._session: AsyncSession | None = None
        self.repositories: dict[str, object] = {}

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        self.repositories = {name: factory(self._session) for name, factory in self._repository_factories.items()}
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: object | None) -> None:
        if self._session is not None:
            await self._session.close()
        self._session = None
        self.repositories = {}

    async def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("Unit of work is not active")
        await self._session.commit()

    async def rollback(self) -> None:
        if self._session is None:
            raise RuntimeError("Unit of work is not active")
        await self._session.rollback()

    def get_repository(self, name: str) -> Any:
        return self.repositories[name]