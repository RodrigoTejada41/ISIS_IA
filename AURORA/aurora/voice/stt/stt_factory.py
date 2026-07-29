from __future__ import annotations

from pathlib import Path

from aurora.core.config import AuroraConfig
from aurora.voice.stt.whisper_local import WhisperCppSTTEngine


def build_stt_engine(config: AuroraConfig) -> WhisperCppSTTEngine:
    return WhisperCppSTTEngine(Path(config.voice.stt_binary_path), Path(config.voice.stt_model_path), device="cuda" if config.voice.use_gpu else "cpu")

