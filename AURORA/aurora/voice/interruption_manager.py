from __future__ import annotations

import time

from aurora.voice.vad_service import VoiceActivityDetector


class InterruptionManager:
    def __init__(self, vad: VoiceActivityDetector | None = None, enabled: bool = True, cooldown_seconds: float = 0.7) -> None:
        self.vad = vad or VoiceActivityDetector()
        self.enabled = enabled
        self.cooldown_seconds = cooldown_seconds
        self.speaking_started_at = 0.0

    def mark_speaking_started(self) -> None:
        self.speaking_started_at = time.time()

    def should_interrupt(self, microphone_audio: bytes) -> bool:
        if not self.enabled:
            return False
        if time.time() - self.speaking_started_at < self.cooldown_seconds:
            return False
        return self.vad.has_voice(microphone_audio)

