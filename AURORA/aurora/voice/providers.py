from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from aurora.voice.text import prepare_text_for_speech


class WakeWordProvider(Protocol):
    def detect(self, audio: bytes) -> bool: ...


class SpeechToTextProvider(Protocol):
    def transcribe(self, audio: bytes, language: str = "pt-BR") -> str: ...
    def cancel(self) -> None: ...


class TextToSpeechProvider(Protocol):
    def list_voices(self) -> list[str]: ...
    def synthesize(self, text: str, voice: str, speed: float = 1.0, volume: float = 1.0) -> Path: ...
    def stop(self) -> None: ...


@dataclass
class MockWakeWordProvider:
    keyword: str = "aurora"

    def detect(self, audio: bytes) -> bool:
        return self.keyword.encode("utf-8").lower() in audio.lower()


@dataclass
class MockSpeechToTextProvider:
    transcript: str = "teste de voz"
    cancelled: bool = False

    def transcribe(self, audio: bytes, language: str = "pt-BR") -> str:
        if self.cancelled:
            return ""
        if not audio:
            raise ValueError("empty audio")
        return self.transcript

    def cancel(self) -> None:
        self.cancelled = True


@dataclass
class MockTextToSpeechProvider:
    tmp_dir: Path
    stopped: bool = False

    def list_voices(self) -> list[str]:
        return ["pt-BR-female-mock"]

    def synthesize(self, text: str, voice: str, speed: float = 1.0, volume: float = 1.0) -> Path:
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        out = self.tmp_dir / "tts_mock.wav"
        speech_text = prepare_text_for_speech(text)
        out.write_bytes(f"voice={voice};speed={speed};volume={volume};text={speech_text}".encode("utf-8"))
        return out

    def stop(self) -> None:
        self.stopped = True
