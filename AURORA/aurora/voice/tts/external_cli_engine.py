from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path

from aurora.voice.text_normalizer import PortugueseSpeechNormalizer
from aurora.voice.tts.base_tts import TTSEngineInfo, TTSResult
from aurora.voice.tts.piper_engine import AudioCache


class ExternalCliTTSEngine:
    def __init__(
        self,
        name: str,
        model_dir: Path,
        output_dir: Path,
        command_args: list[str] | None = None,
        voice: str = "",
        supports_streaming: bool = False,
        supports_emotion: bool = False,
        cache: AudioCache | None = None,
    ) -> None:
        self.name = name
        self.model_dir = model_dir
        self.output_dir = output_dir
        self.command_args = command_args or self._load_manifest_command()
        self.voice = voice or self._load_manifest_voice()
        self.supports_streaming = supports_streaming
        self.supports_emotion = supports_emotion
        self.cache = cache
        self.normalizer = PortugueseSpeechNormalizer()
        self._loaded = False

    def _manifest_path(self) -> Path:
        return self.model_dir / "tts_manifest.json"

    def _load_manifest(self) -> dict:
        path = self._manifest_path()
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _load_manifest_command(self) -> list[str]:
        command = self._load_manifest().get("command", [])
        return command if isinstance(command, list) else []

    def _load_manifest_voice(self) -> str:
        voice = self._load_manifest().get("voice", "")
        return voice if isinstance(voice, str) else ""

    def _error(self) -> str:
        if not self.command_args:
            return f"{self.name} command not configured"
        executable = self.command_args[0]
        if Path(executable).exists() or shutil.which(executable):
            return ""
        return f"{self.name} executable not found: {executable}"

    def _render_args(self, text: str, output_path: Path, emotion: str, speed: float, volume: float) -> list[str]:
        values = {
            "text": text,
            "output": str(output_path),
            "model_dir": str(self.model_dir),
            "voice": self.voice,
            "emotion": emotion,
            "speed": str(speed),
            "volume": str(volume),
        }
        return [arg.format(**values) for arg in self.command_args]

    def load(self) -> None:
        error = self._error()
        if error:
            raise RuntimeError(error)
        self._loaded = True

    def synthesize(self, text: str, output_path: Path | None = None, emotion: str = "neutral", speed: float = 1.0, volume: float = 1.0) -> TTSResult:
        started = time.time()
        normalized = self.normalizer.normalize(text)
        voice = self.voice or self.name
        cache_key = self.cache.key(normalized, self.name, voice, speed, emotion) if self.cache else ""
        cached = self.cache.get(cache_key) if self.cache and cache_key else None
        if cached:
            return TTSResult(cached, self.name, voice, int((time.time() - started) * 1000), cached=True)

        self.load()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        target = output_path or self.output_dir / f"{self.name}_{int(time.time() * 1000)}.wav"
        args = self._render_args(normalized, target, emotion, speed, volume)
        completed = subprocess.run(args, cwd=str(self.model_dir) if self.model_dir.exists() else None, capture_output=True, text=True, timeout=120)
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "").strip()
            raise RuntimeError(f"{self.name} failed: {detail}")
        if not target.exists() or target.stat().st_size <= 0:
            raise RuntimeError(f"{self.name} did not create audio output")
        audio_path = self.cache.put(cache_key, target) if self.cache and cache_key else target
        return TTSResult(audio_path, self.name, voice, int((time.time() - started) * 1000))

    def stop(self) -> None:
        return

    def is_available(self) -> bool:
        return self._error() == ""

    def unload(self) -> None:
        self._loaded = False

    def info(self) -> TTSEngineInfo:
        error = self._error()
        return TTSEngineInfo(
            name=self.name,
            voice=self.voice,
            loaded=self._loaded,
            available=not error,
            supports_streaming=self.supports_streaming,
            supports_emotion=self.supports_emotion,
            license_note="local/offline when configured model license permits use",
            error=error,
        )
