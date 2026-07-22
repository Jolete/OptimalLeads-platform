from __future__ import annotations

import logging
import os
from pathlib import Path
import sys

from core_infrastructure.observability import TraceContextFilter


def _parse_handlers(raw_value: str | None) -> set[str]:
    if not raw_value:
        return {"console"}
    handlers = {item.strip().lower() for item in raw_value.split(",") if item.strip()}
    if not handlers:
        return {"console"}
    if "both" in handlers:
        return {"console", "file"}
    return handlers


def configure_logging(level: int = logging.INFO, *, handlers: set[str] | None = None, log_file_path: str | None = None) -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if root_logger.handlers:
        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)

    resolved_handlers = handlers if handlers is not None else _parse_handlers(os.getenv("LOG_HANDLERS"))
    resolved_log_file_path = log_file_path or os.getenv("LOG_FILE_PATH")

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s [trace=%(trace_id)s span=%(span_id)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if "console" in resolved_handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.addFilter(TraceContextFilter())
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    if "file" in resolved_handlers:
        if not resolved_log_file_path:
            raise ValueError("LOG_FILE_PATH is required when LOG_HANDLERS includes 'file'")
        log_path = Path(resolved_log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.addFilter(TraceContextFilter())
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)