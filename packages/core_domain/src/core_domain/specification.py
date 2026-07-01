from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Protocol, TypeVar

T = TypeVar("T")


class Specification(Protocol[T]):
    def is_satisfied_by(self, candidate: T) -> bool:
        ...


@dataclass(frozen=True, slots=True)
class PredicateSpecification(Generic[T]):
    predicate: Callable[[T], bool]

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.predicate(candidate)

    def __invert__(self) -> "PredicateSpecification[T]":
        return PredicateSpecification(lambda candidate: not self.is_satisfied_by(candidate))
