from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from aurora.core.audit import AuditLogger
from aurora.core.config import AuroraConfig
from aurora.voice.audio import AudioInputManager, AudioOutputManager
from aurora.voice.emotion_analyzer import EmotionAnalyzer
from aurora.voice.interruption_manager import InterruptionManager
from aurora.voice.speech_queue import SpeechQueue
from aurora.voice.tts.tts_factory import build_tts_engines
from aurora.voice.voice_router import VoiceRouter


class VoiceManager:
    def __init__(self, config: AuroraConfig, audit: AuditLogger) -> None:
        self.config = config
        self.audit = audit
        self.audio_out = AudioOutputManager()
        self.queue = SpeechQueue(self.audio_out)
        self.emotions = EmotionAnalyzer()
        self.interruptions = InterruptionManager(enabled=config.voice.allow_interruption)
        self.router = VoiceRouter(build_tts_engines(config), audit)

    def speak(self, text: str, emotion: str | None = None, play: bool = False) -> dict:
        style = emotion or self.emotions.classify(text)
        result = self.router.synthesize(text, emotion=style, speed=self.config.voice.speed, volume=self.config.voice.volume)
        if not result:
            return {"ok": False, "error": "no local TTS engine available", "audio_path": None, "emotion": style}
        if play:
            self.queue.enqueue(result.audio_path)
            self.interruptions.mark_speaking_started()
            self.queue.play()
        return {"ok": True, "audio_path": str(result.audio_path), "engine": result.engine, "voice": result.voice, "elapsed_ms": result.elapsed_ms, "cached": result.cached, "emotion": style}

    def stop(self) -> None:
        self.queue.stop()
        for engine in self.router.engines:
            engine.stop()

    def status(self) -> dict:
        audio_in = AudioInputManager(device_name=self.config.voice.microphone_device or None)
        return {
            "language": self.config.voice.language,
            "tts_engine": self.config.voice.tts_engine,
            "stt_engine": self.config.voice.stt_engine,
            "selected_voice": self.config.voice.selected_voice,
            "output_device": self.config.voice.output_device,
            "microphone_device": self.config.voice.microphone_device,
            "speed": self.config.voice.speed,
            "volume": self.config.voice.volume,
            "allow_interruption": self.config.voice.allow_interruption,
            "strict_offline": self.config.voice.strict_offline,
            "audio_cache_enabled": self.config.voice.audio_cache_enabled,
            "queue_state": self.queue.state.value,
            "microphones": audio_in.list_devices(),
            "engines": self.router.status(),
        }

