from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from time import monotonic


class MemoryRateLimiter:
    def __init__(self) -> None:
        self._buckets: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def hit(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        now = monotonic()
        async with self._lock:
            bucket = self._buckets[key]
            threshold = now - window_seconds
            while bucket and bucket[0] <= threshold:
                bucket.popleft()

            if len(bucket) >= limit:
                retry_after = max(1, int(window_seconds - (now - bucket[0])))
                return False, retry_after

            bucket.append(now)
            return True, 0


rate_limiter = MemoryRateLimiter()
