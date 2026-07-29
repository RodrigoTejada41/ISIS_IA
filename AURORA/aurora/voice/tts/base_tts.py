from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(slots=True)
class TTSEngineInfo:
    name: str
    voice: str
    language: str = "pt-BR"
    loaded: bool = False
    available: bool = False
    supports_streaming: bool = False
    supports_emotion: bool = False
    license_note: str = "local/offline when model is installed"
    error: str = ""


@dataclass(slots=True)
class TTSResult:
    audio_path: Path
    engine: str
    voice: str
    elapsed_ms: int
    cached: bool = False


class BaseTTSEngine(Protocol):
    name: str

    def load(self) -> None: ...

    def synthesize(self, text: str, output_path: Path | None = None, emotion: str = "neutral", speed: float = 1.0, volume: float = 1.0) -> TTSResult: ...

    def stop(self) -> None: ...

    def is_available(self) -> bool: ...

    def unload(self) -> None: ...

    def info(self) -> TTSEngineInfo: ...

