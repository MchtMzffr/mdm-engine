"""RateLimiter (token bucket); exponential backoff with jitter on 429."""

import time
import random
from dataclasses import dataclass, field


@dataclass
class RateLimiter:
    """
    Token bucket: refill rate per second, max tokens.

    Initial token policy (default): tokens start at 0.0. The first allow() call may deny
    until refill adds at least one token. For "start full" behaviour, pass initial_tokens
    (e.g. capacity) when constructing, or use RateLimiter(rate=..., capacity=n, tokens=float(n)).
    """

    rate: float  # tokens per second
    capacity: int
    tokens: float = field(default=0.0)
    last_refill: float = field(default_factory=time.monotonic)

    def __post_init__(self) -> None:
        """Clamp tokens to [0, capacity]."""
        self.tokens = max(0.0, min(float(self.capacity), self.tokens))

    def _refill(self) -> None:
        now = time.monotonic()
        self.tokens = min(
            self.capacity,
            self.tokens + (now - self.last_refill) * self.rate,
        )
        self.last_refill = now

    def allow(self) -> bool:
        """Consume one token if available; return True if allowed."""
        self._refill()
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


def backoff_with_jitter(attempt: int, base_sec: float = 1.0, max_sec: float = 60.0) -> float:
    """Exponential backoff + jitter for 429/retries."""
    sec = min(max_sec, base_sec * (2**attempt))
    return sec * (0.5 + random.random() * 0.5)
