from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from agent.models import ExtractionResult


class Extractor(ABC):
    mode: str

    @abstractmethod
    def extract(self, snapshot_id: str, text_path: Path, image_path: Path | None = None) -> ExtractionResult:
        raise NotImplementedError

