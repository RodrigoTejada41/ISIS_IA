from __future__ import annotations


class VoiceActivityDetector:
    def __init__(self, min_bytes: int = 128, threshold: int = 4) -> None:
        self.min_bytes = min_bytes
        self.threshold = threshold

    def has_voice(self, audio: bytes) -> bool:
        if len(audio or b"") < self.min_bytes:
            return False
        sample = audio[:4096]
        average = sum(abs(byte - 128) for byte in sample) / max(1, len(sample))
        return average >= self.threshold

