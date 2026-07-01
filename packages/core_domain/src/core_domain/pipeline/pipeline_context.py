from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PipelineContext:
    request_name: str
    correlation_id: str | None = None