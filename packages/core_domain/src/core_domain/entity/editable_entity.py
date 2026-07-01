from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, TypeVar

from core_domain.entity.entity import Entity
from core_domain.types import EntityId


IdType = TypeVar("IdType", bound=EntityId)


@dataclass(slots=True)
class EditableEntity(Entity[IdType], Generic[IdType]):
    is_editable: bool = field(default=True, kw_only=True)