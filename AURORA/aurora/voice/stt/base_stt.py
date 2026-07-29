from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class STTEngineInfo:
    name: str
    model: str
    language: str = "pt-BR"
    available: bool = False
    device: str = "cpu"
    error: str = ""


@dataclass(slots=True)
class STTResult:
    text: str
    engine: str
    elapsed_ms: int


class BaseSTTEngine(Protocol):
    name: str

    def transcribe(self, audio: bytes, language: str = "pt-BR") -> STTResult: ...

    def cancel(self) -> None: ...

    def is_available(self) -> bool: ...

    def info(self) -> STTEngineInfo: ...

