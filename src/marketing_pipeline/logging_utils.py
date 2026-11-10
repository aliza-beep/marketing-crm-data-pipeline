from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class JsonLineHandler(logging.Handler):
    def __init__(self, path: Path):
        super().__init__()
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, record: logging.LogRecord) -> None:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("run_id", "source", "rows", "stage", "error_type"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, default=str) + "\n")


def configure_logging(path: Path, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("marketing_pipeline")
    logger.setLevel(level)
    existing_json = [handler for handler in logger.handlers if isinstance(handler, JsonLineHandler)]
    if not any(handler.path.resolve() == path.resolve() for handler in existing_json):
        for handler in existing_json:
            logger.removeHandler(handler)
            handler.close()
        logger.addHandler(JsonLineHandler(path))
    if not any(type(handler) is logging.StreamHandler for handler in logger.handlers):
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
        logger.addHandler(console)
    return logger

