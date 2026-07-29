from __future__ import annotations

import time
from collections import deque


class RateLimiter:
    def __init__(self, per_minute: int, per_hour: int) -> None:
        self.per_minute = per_minute
        self.per_hour = per_hour
        self.events: deque[float] = deque()

    def allow(self) -> bool:
        now = time.time()
        while self.events and now - self.events[0] > 3600:
            self.events.popleft()
        minute_count = len([item for item in self.events if now - item <= 60])
        if minute_count >= self.per_minute or len(self.events) >= self.per_hour:
            return False
        self.events.append(now)
        return True
