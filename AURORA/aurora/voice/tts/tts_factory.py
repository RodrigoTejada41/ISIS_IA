from __future__ import annotations

from pathlib import Path

from aurora.core.config import AuroraConfig
from aurora.voice.tts.chatterbox_engine import ChatterboxTTSEngine
from aurora.voice.tts.kokoro_engine import KokoroTTSEngine
from aurora.voice.tts.piper_engine import AudioCache, PiperTTSEngine


def build_tts_engines(config: AuroraConfig) -> list[object]:
    output_dir = Path(config.paths.temporary_dir)
    cache = AudioCache(Path(config.paths.cache_dir) / "audio", max_files=config.voice.audio_cache_max_files) if config.voice.audio_cache_enabled else None
    engines: list[object] = [
        KokoroTTSEngine(Path(config.voice.kokoro_model_dir), output_dir, command_args=config.voice.kokoro_command, voice=config.voice.kokoro_voice, cache=cache),
        ChatterboxTTSEngine(Path(config.voice.chatterbox_model_dir), output_dir, command_args=config.voice.chatterbox_command, voice=config.voice.chatterbox_voice, cache=cache),
        PiperTTSEngine(Path(config.voice.piper_binary_path), Path(config.voice.piper_voice_path), output_dir, cache=cache),
    ]
    preferred = config.voice.tts_engine
    return sorted(engines, key=lambda engine: 0 if getattr(engine, "name", "") == preferred else 1)
