from __future__ import annotations

import time
from collections import defaultdict, deque


class SlidingWindowLimiter:
    def __init__(self, rate: int, window_s: float) -> None:
        self.rate = rate
        self.window = window_s
        self.events: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        q = self.events[key]
        while q and now - q[0] > self.window:
            q.popleft()
        if len(q) >= self.rate:
            return False
        q.append(now)
        return True
