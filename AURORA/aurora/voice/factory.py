from __future__ import annotations

from pathlib import Path

from aurora.core.audit import AuditLogger
from aurora.core.config import AuroraConfig
from aurora.voice.audio import AudioInputManager, AudioOutputManager
from aurora.voice.local_providers import ConfiguredWakeWordProvider, PiperTextToSpeechProvider, WhisperCppSpeechToTextProvider
from aurora.voice.providers import MockSpeechToTextProvider, MockTextToSpeechProvider
from aurora.voice.session import VoiceSessionConfig, VoiceSessionManager


def build_voice_session(config: AuroraConfig, audit: AuditLogger, transcript: str = "status") -> VoiceSessionManager:
    wake = ConfiguredWakeWordProvider(config.voice.wake_word, config.voice.wake_word_enabled)
    if config.voice.stt_engine == "whisper_cpp":
        stt = WhisperCppSpeechToTextProvider(Path(config.voice.stt_binary_path), Path(config.voice.stt_model_path))
    else:
        stt = MockSpeechToTextProvider(transcript)
    if config.voice.tts_engine == "piper":
        tts = PiperTextToSpeechProvider(Path(config.voice.piper_binary_path), Path(config.voice.piper_voice_path), Path(config.paths.temporary_dir))
    else:
        tts = MockTextToSpeechProvider(Path(config.paths.temporary_dir))
    session_config = VoiceSessionConfig(
        language=config.voice.language,
        selected_voice=config.voice.selected_voice,
        response_mode=config.voice.response_mode,
    )
    return VoiceSessionManager(
        wake=wake,
        stt=stt,
        tts=tts,
        audio_in=AudioInputManager(),
        audio_out=AudioOutputManager(),
        audit=audit,
        config=session_config,
    )
