from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class TokenBucket:
    capacity: int
    refill_per_sec: float
    tokens: float
    last_ts: float

    def allow(self, cost: float = 1.0) -> bool:
        now = time.time()
        elapsed = max(0.0, now - self.last_ts)
        self.last_ts = now
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_per_sec)
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False


class RateLimiter:
    def __init__(self, *, capacity: int, refill_per_sec: float):
        self.capacity = capacity
        self.refill_per_sec = refill_per_sec
        self._buckets: dict[str, TokenBucket] = {}

    def allow(self, key: str, cost: float = 1.0) -> bool:
        b = self._buckets.get(key)
        if not b:
            b = TokenBucket(capacity=self.capacity, refill_per_sec=self.refill_per_sec, tokens=float(self.capacity), last_ts=time.time())
            self._buckets[key] = b
        return b.allow(cost=cost)

