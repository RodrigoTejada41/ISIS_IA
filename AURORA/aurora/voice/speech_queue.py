from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from aurora.voice.audio import AudioOutputManager


class SpeechQueueState(str, Enum):
    IDLE = "idle"
    GENERATING = "generating"
    SPEAKING = "speaking"
    PAUSED = "paused"
    INTERRUPTED = "interrupted"
    ERROR = "error"


@dataclass
class SpeechQueue:
    audio_out: AudioOutputManager
    state: SpeechQueueState = SpeechQueueState.IDLE
    last_audio: Path | None = None

    def enqueue(self, path: Path) -> None:
        self.audio_out.enqueue(path)

    def play(self) -> Path | None:
        self.state = SpeechQueueState.SPEAKING
        self.last_audio = self.audio_out.play_next()
        if self.last_audio is None:
            self.state = SpeechQueueState.IDLE
        return self.last_audio

    def stop(self) -> None:
        self.audio_out.stop()
        self.state = SpeechQueueState.INTERRUPTED

    def clear(self) -> None:
        self.audio_out.stop()
        self.audio_out.reset()
        self.state = SpeechQueueState.IDLE

    def replay_last(self) -> Path | None:
        if self.last_audio:
            self.enqueue(self.last_audio)
            return self.play()
        return None

