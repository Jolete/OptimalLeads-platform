from __future__ import annotations

from typing import Generic, TypeVar

RequestT = TypeVar("RequestT")
ResponseT = TypeVar("ResponseT")


class UseCase(Generic[RequestT, ResponseT]):
    async def execute(self, request: RequestT) -> ResponseT:
        raise NotImplementedError
