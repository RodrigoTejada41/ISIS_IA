from __future__ import annotations

import hashlib
import json
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

from aurora.voice.local_providers import PiperTextToSpeechProvider
from aurora.voice.text_normalizer import PortugueseSpeechNormalizer
from aurora.voice.tts.base_tts import TTSEngineInfo, TTSResult


@dataclass(slots=True)
class AudioCache:
    cache_dir: Path
    max_files: int = 200

    def key(self, text: str, engine: str, voice: str, speed: float, emotion: str) -> str:
        payload = json.dumps({"text": text, "engine": engine, "voice": voice, "speed": speed, "emotion": emotion, "v": 1}, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Path | None:
        path = self.cache_dir / f"{key}.wav"
        return path if path.exists() and path.stat().st_size > 0 else None

    def put(self, key: str, source: Path) -> Path:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        target = self.cache_dir / f"{key}.wav"
        if source.resolve() != target.resolve():
            shutil.copy2(source, target)
        self.prune()
        return target

    def clear(self) -> int:
        count = 0
        if self.cache_dir.exists():
            for path in self.cache_dir.glob("*.wav"):
                path.unlink(missing_ok=True)
                count += 1
        return count

    def prune(self) -> None:
        files = sorted(self.cache_dir.glob("*.wav"), key=lambda p: p.stat().st_mtime, reverse=True)
        for path in files[self.max_files :]:
            path.unlink(missing_ok=True)


class PiperTTSEngine:
    name = "piper"

    def __init__(self, binary_path: Path, voice_path: Path, output_dir: Path, cache: AudioCache | None = None) -> None:
        self.binary_path = binary_path
        self.voice_path = voice_path
        self.output_dir = output_dir
        self.cache = cache
        self.normalizer = PortugueseSpeechNormalizer()
        self._provider = PiperTextToSpeechProvider(binary_path, voice_path, output_dir)
        self._loaded = False

    def load(self) -> None:
        self._provider._check_environment()
        self._loaded = True

    def synthesize(self, text: str, output_path: Path | None = None, emotion: str = "neutral", speed: float = 1.0, volume: float = 1.0) -> TTSResult:
        started = time.time()
        normalized = self.normalizer.normalize(text)
        voice = self.voice_path.stem
        cache_key = self.cache.key(normalized, self.name, voice, speed, emotion) if self.cache else ""
        cached = self.cache.get(cache_key) if self.cache and cache_key else None
        if cached:
            return TTSResult(cached, self.name, voice, int((time.time() - started) * 1000), cached=True)
        self.load()
        generated = self._provider.synthesize(normalized, voice, speed=speed, volume=volume)
        audio_path = output_path or generated
        if output_path and generated != output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(generated), str(output_path))
        if self.cache and cache_key:
            audio_path = self.cache.put(cache_key, audio_path)
        return TTSResult(audio_path, self.name, voice, int((time.time() - started) * 1000))

    def stop(self) -> None:
        self._provider.stop()

    def is_available(self) -> bool:
        return self.binary_path.exists() and self.voice_path.exists()

    def unload(self) -> None:
        self._loaded = False

    def info(self) -> TTSEngineInfo:
        return TTSEngineInfo(
            name=self.name,
            voice=self.voice_path.name,
            loaded=self._loaded,
            available=self.is_available(),
            supports_streaming=False,
            supports_emotion=False,
            license_note="Piper local; model license depends on installed voice",
            error="" if self.is_available() else "piper binary or voice missing",
        )

