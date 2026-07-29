from __future__ import annotations

import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from aurora.voice.text import prepare_text_for_speech


@dataclass(slots=True)
class WhisperCppSpeechToTextProvider:
    binary_path: Path
    model_path: Path
    timeout_seconds: int = 60
    cancelled: bool = False

    def transcribe(self, audio: bytes, language: str = "pt-BR") -> str:
        self._check_environment()
        if self.cancelled:
            return ""
        if not audio:
            raise ValueError("empty audio")
        with tempfile.TemporaryDirectory(prefix="aurora_whisper_") as tmp:
            audio_path = Path(tmp) / "input.wav"
            audio_path.write_bytes(audio)
            proc = subprocess.run(
                [
                    str(self.binary_path),
                    "-m",
                    str(self.model_path),
                    "-f",
                    str(audio_path),
                    "-l",
                    language.split("-")[0],
                    "-nt",
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or "whisper.cpp failed")
        return proc.stdout.strip()

    def cancel(self) -> None:
        self.cancelled = True

    def _check_environment(self) -> None:
        if not self.binary_path.exists():
            raise FileNotFoundError(f"whisper.cpp binary not found: {self.binary_path}")
        if not self.model_path.exists():
            raise FileNotFoundError(f"whisper.cpp model not found: {self.model_path}")


@dataclass(slots=True)
class PiperTextToSpeechProvider:
    binary_path: Path
    voice_path: Path
    output_dir: Path
    timeout_seconds: int = 60
    stopped: bool = False

    def list_voices(self) -> list[str]:
        return [self.voice_path.name] if self.voice_path.exists() else []

    def synthesize(self, text: str, voice: str, speed: float = 1.0, volume: float = 1.0) -> Path:
        self._check_environment()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        speech_text = prepare_text_for_speech(text)
        output = self.output_dir / f"piper_output_{int(time.time() * 1000)}.wav"
        proc = subprocess.run(
            [str(self.binary_path), "--model", str(self.voice_path), "--output_file", str(output)],
            input=speech_text,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or "piper failed")
        return output

    def stop(self) -> None:
        self.stopped = True

    def _check_environment(self) -> None:
        if not self.binary_path.exists():
            raise FileNotFoundError(f"piper binary not found: {self.binary_path}")
        if not self.voice_path.exists():
            raise FileNotFoundError(f"piper voice not found: {self.voice_path}")


@dataclass(slots=True)
class ConfiguredWakeWordProvider:
    keyword: str = "aurora"
    enabled: bool = True

    def detect(self, audio: bytes) -> bool:
        if not self.enabled:
            return True
        return self.keyword.encode("utf-8").lower() in audio.lower()
