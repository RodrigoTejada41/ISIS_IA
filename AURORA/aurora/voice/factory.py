from __future__ import annotations

from pathlib import Path

from aurora.core.audit import AuditLogger
from aurora.core.config import AuroraConfig
from aurora.voice.audio import AudioInputManager, AudioOutputManager
from aurora.voice.local_providers import ConfiguredWakeWordProvider, PiperTextToSpeechProvider, WhisperCppSpeechToTextProvider
from aurora.voice.providers import MockSpeechToTextProvider, MockTextToSpeechProvider
from aurora.voice.session import VoiceSessionConfig, VoiceSessionManager
from aurora.voice.voice_manager import VoiceManager


class RoutedTextToSpeechProvider:
    def __init__(self, manager: VoiceManager) -> None:
        self.manager = manager
        self.stopped = False

    def list_voices(self) -> list[str]:
        voices: list[str] = []
        for engine in self.manager.router.engines:
            info = engine.info()
            if info.voice:
                voices.append(info.voice)
        return voices

    def synthesize(self, text: str, voice: str, speed: float = 1.0, volume: float = 1.0):
        result = self.manager.router.synthesize(text, emotion=self.manager.emotions.classify(text), speed=speed, volume=volume)
        if not result:
            fallback = MockTextToSpeechProvider(Path(self.manager.config.paths.temporary_dir))
            return fallback.synthesize(text, voice, speed=speed, volume=volume)
        return result.audio_path

    def stop(self) -> None:
        self.stopped = True
        self.manager.stop()


def build_voice_session(config: AuroraConfig, audit: AuditLogger, transcript: str = "status") -> VoiceSessionManager:
    wake = ConfiguredWakeWordProvider(config.voice.wake_word, config.voice.wake_word_enabled)
    if config.voice.stt_engine == "whisper_cpp":
        stt = WhisperCppSpeechToTextProvider(Path(config.voice.stt_binary_path), Path(config.voice.stt_model_path))
    else:
        stt = MockSpeechToTextProvider(transcript)
    if config.voice.tts_engine in {"piper", "kokoro", "chatterbox"}:
        tts = RoutedTextToSpeechProvider(VoiceManager(config, audit))
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
