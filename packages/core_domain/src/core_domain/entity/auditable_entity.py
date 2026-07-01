from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, TypeVar

from core_domain.entity.entity import Entity
from core_domain.types import EntityId


IdType = TypeVar("IdType", bound=EntityId)


@dataclass(slots=True)
class AuditableEntity(Entity[IdType], Generic[IdType]):
    created_at: object | None = field(default=None, kw_only=True)
    created_by: str | None = field(default=None, kw_only=True)
    updated_at: object | None = field(default=None, kw_only=True)
    updated_by: str | None = field(default=None, kw_only=True)