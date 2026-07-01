from __future__ import annotations

from typing import Callable, Iterable, Protocol, TypeVar

from core_domain.specification import Specification

T = TypeVar("T")
IdType = TypeVar("IdType")
ResultType = TypeVar("ResultType")
ProjectionType = TypeVar("ProjectionType")
OrderKeyType = TypeVar("OrderKeyType")


class Repository(Protocol[T, IdType]):
    async def add(self, entity: T) -> IdType:
        ...

    async def get(self, id_: IdType) -> T | None:
        ...

    async def update(self, entity: T) -> None:
        ...

    async def remove(self, entity: T) -> None:
        ...

    async def exists(self, id_: IdType) -> bool:
        ...

    async def list(self) -> list[T]:
        ...

    async def search(self, criteria: Specification[T]) -> list[T]:
        ...

    async def count(self, criteria: Specification[T] | None = None) -> int:
        ...

    async def first_or_none(self, criteria: Specification[T]) -> T | None:
        ...

    async def get_many(self, ids: Iterable[IdType]) -> list[T]:
        ...

    async def project_to(self, projection: Callable[[T], ProjectionType]) -> list[ProjectionType]:
        ...

    async def project_one(self, criteria: Specification[T], projection: Callable[[T], ResultType]) -> ResultType | None:
        ...

    async def any(self, criteria: Specification[T]) -> bool:
        ...

    async def all(self) -> list[T]:
        ...

    async def delete_by_id(self, id_: IdType) -> None:
        ...

    async def delete_many(self, ids: Iterable[IdType]) -> None:
        ...

    async def save(self, entity: T) -> T:
        ...

    async def upsert(self, entity: T) -> T:
        ...

    async def order_by(self, key_selector: Callable[[T], OrderKeyType]) -> list[T]:
        ...
