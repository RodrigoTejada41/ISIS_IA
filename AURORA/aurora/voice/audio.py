from __future__ import annotations

import queue
import winsound
import threading
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AudioInputManager:
    device_name: str | None = None
    max_record_seconds: int = 30
    silence_threshold: float = 0.02

    def list_devices(self) -> list[str]:
        return ["mock-microphone"]

    def test_microphone(self) -> bool:
        return self.device_name in {None, "mock-microphone"}

    def capture(self) -> bytes:
        if not self.test_microphone():
            raise RuntimeError("microphone unavailable")
        return b"aurora comando de teste"


@dataclass
class AudioOutputManager:
    playback_queue: queue.Queue[Path] = field(default_factory=queue.Queue)
    stop_event: threading.Event = field(default_factory=threading.Event)
    played: list[Path] = field(default_factory=list)

    def enqueue(self, path: Path) -> None:
        self.playback_queue.put(path)

    def play_next(self) -> Path | None:
        if self.stop_event.is_set() or self.playback_queue.empty():
            return None
        path = self.playback_queue.get_nowait()
        self.played.append(path)
        if path.suffix.lower() == ".wav" and path.exists():
            winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        return path

    def stop(self) -> None:
        self.stop_event.set()
        winsound.PlaySound(None, winsound.SND_PURGE)
        while not self.playback_queue.empty():
            self.playback_queue.get_nowait()

    def reset(self) -> None:
        self.stop_event.clear()
