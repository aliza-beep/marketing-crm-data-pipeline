from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass(frozen=True)
class ExtractResult:
    source: str
    rows: list[dict[str, Any]]
    simulated: bool = True


class Connector(ABC):
    """Interface shared by simulated and future authenticated connectors."""

    source: str

    @abstractmethod
    def extract(self, start_date: date, end_date: date) -> ExtractResult:
        raise NotImplementedError

