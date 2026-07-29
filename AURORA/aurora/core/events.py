from __future__ import annotations

import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True, slots=True)
class Event:
    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)


EventHandler = Callable[[Event], None]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._history: list[Event] = []

    def subscribe(self, name: str, handler: EventHandler) -> None:
        self._handlers[name].append(handler)

    def publish(self, event: Event) -> None:
        self._history.append(event)
        for handler in self._handlers.get(event.name, []):
            handler(event)
        for handler in self._handlers.get("*", []):
            handler(event)

    def history(self) -> list[Event]:
        return list(self._history)
