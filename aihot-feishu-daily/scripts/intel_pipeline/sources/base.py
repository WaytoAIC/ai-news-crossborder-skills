from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SourceContext:
    repo_root: Path
    days: int


@dataclass
class SourceResult:
    items: list[dict]
    packet: dict


class SourceAdapter:
    def __init__(self, config: dict, context: SourceContext) -> None:
        self.config = config
        self.context = context

    def fetch(self) -> SourceResult:
        raise NotImplementedError

