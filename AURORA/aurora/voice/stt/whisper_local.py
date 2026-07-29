from __future__ import annotations

import time
from pathlib import Path

from aurora.voice.local_providers import WhisperCppSpeechToTextProvider
from aurora.voice.stt.base_stt import STTEngineInfo, STTResult


class WhisperCppSTTEngine:
    name = "whisper_cpp"

    def __init__(self, binary_path: Path, model_path: Path, device: str = "auto") -> None:
        self.binary_path = binary_path
        self.model_path = model_path
        self.device = device
        self._provider = WhisperCppSpeechToTextProvider(binary_path, model_path)

    def transcribe(self, audio: bytes, language: str = "pt-BR") -> STTResult:
        started = time.time()
        text = self._provider.transcribe(audio, language)
        return STTResult(text=text, engine=self.name, elapsed_ms=int((time.time() - started) * 1000))

    def cancel(self) -> None:
        self._provider.cancel()

    def is_available(self) -> bool:
        return self.binary_path.exists() and self.model_path.exists()

    def info(self) -> STTEngineInfo:
        return STTEngineInfo(
            name=self.name,
            model=self.model_path.name,
            available=self.is_available(),
            device=self.device,
            error="" if self.is_available() else "whisper.cpp binary or model missing",
        )

