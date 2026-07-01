from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Callable, Generic, Iterable, TypeVar

from sqlalchemy import select

from core_domain.repository import Repository
from core_domain.specification import Specification

T = TypeVar("T")
IdType = TypeVar("IdType")
ModelType = TypeVar("ModelType")


class SqlAlchemyRepository(Repository[T, IdType], Generic[T, IdType]):
    """Generic SQLAlchemy-backed CRUD repository.

    This is the reusable adapter over SQLAlchemy, not a database-specific
    implementation. It behaves the same behind SQL Server, SQLite, Oracle or
    any other backend supported by SQLAlchemy.

    Concrete projects can inherit from it only when they need custom queries,
    custom mappings or additional logic.
    """

    def __init__(
        self,
        session: Any,
        model_type: type[ModelType],
        entity_factory: Callable[[ModelType], T],
        model_factory: Callable[[T], ModelType] | None = None,
        id_extractor: Callable[[ModelType], IdType] | None = None,
        auto_commit: bool = True,
    ) -> None:
        self._session = session
        self._model_type = model_type
        self._entity_factory = entity_factory
        self._model_factory = model_factory or self._default_model_factory
        self._id_extractor = id_extractor or self._default_id_extractor
        self._auto_commit = auto_commit

    async def add(self, entity: T) -> IdType:
        model = self._model_factory(entity)
        self._session.add(model)
        await self._session.flush()
        if self._auto_commit:
            await self._session.commit()
        return self._extract_id(model)

    async def get(self, id_: IdType) -> T | None:
        model = await self._session.get(self._model_type, id_)
        return self._entity_factory(model) if model else None

    async def update(self, entity: T) -> None:
        model = self._model_factory(entity)
        await self._session.merge(model)
        if self._auto_commit:
            await self._session.commit()

    async def remove(self, entity: T) -> None:
        model = self._model_factory(entity)
        await self._session.delete(model)
        if self._auto_commit:
            await self._session.commit()

    async def exists(self, id_: IdType) -> bool:
        return (await self.get(id_)) is not None

    async def list(self) -> list[T]:
        result = await self._session.execute(select(self._model_type))
        models = result.scalars().all()
        return [self._entity_factory(model) for model in models]

    async def search(self, criteria: Specification[T]) -> list[T]:
        return [entity for entity in await self.list() if criteria.is_satisfied_by(entity)]

    async def count(self, criteria: Specification[T] | None = None) -> int:
        entities = await self.list()
        if criteria is None:
            return len(entities)
        return sum(1 for entity in entities if criteria.is_satisfied_by(entity))

    async def first_or_none(self, criteria: Specification[T]) -> T | None:
        for entity in await self.list():
            if criteria.is_satisfied_by(entity):
                return entity
        return None

    async def get_many(self, ids: Iterable[IdType]) -> list[T]:
        return [entity for id_ in ids if (entity := await self.get(id_)) is not None]

    async def project_to(self, projection: Callable[[T], Any]) -> list[Any]:
        return [projection(entity) for entity in await self.list()]

    async def project_one(self, criteria: Specification[T], projection: Callable[[T], Any]) -> Any | None:
        entity = await self.first_or_none(criteria)
        return projection(entity) if entity else None

    async def any(self, criteria: Specification[T]) -> bool:
        return (await self.first_or_none(criteria)) is not None

    async def all(self) -> list[T]:
        return await self.list()

    async def delete_by_id(self, id_: IdType) -> None:
        model = await self._session.get(self._model_type, id_)
        if model is None:
            return
        await self._session.delete(model)
        if self._auto_commit:
            await self._session.commit()

    async def delete_many(self, ids: Iterable[IdType]) -> None:
        for id_ in ids:
            await self.delete_by_id(id_)

    async def save(self, entity: T) -> T:
        model = self._model_factory(entity)
        await self._session.merge(model)
        await self._session.flush()
        if self._auto_commit:
            await self._session.commit()
        return entity

    async def upsert(self, entity: T) -> T:
        model = self._model_factory(entity)
        await self._session.merge(model)
        if self._auto_commit:
            await self._session.commit()
        return entity

    async def order_by(self, key_selector: Callable[[T], Any]) -> list[T]:
        return sorted(await self.list(), key=key_selector)

    def _default_model_factory(self, entity: T) -> ModelType:
        if is_dataclass(entity):
            return self._model_type(**asdict(entity))
        raise TypeError("Entity must be a dataclass or provide a model_factory")

    def _extract_id(self, model: ModelType) -> IdType:
        return self._id_extractor(model)

    def _default_id_extractor(self, model: ModelType) -> IdType:
        if hasattr(model, "id"):
            return getattr(model, "id")
        raise AttributeError("Model must expose an 'id' attribute or provide an id_extractor")

