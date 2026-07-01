from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LeadReadModel:
    id: str
    name: str
    stage: str
