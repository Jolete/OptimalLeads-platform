from __future__ import annotations

from typing import Protocol, TypeVar, runtime_checkable


TResponse = TypeVar("TResponse")


@runtime_checkable
class Command(Protocol[TResponse]):
    __command__: bool