from __future__ import annotations

import logging
import time
from collections import deque

from ai_agent_sdk.exceptions import RateLimitError
from ai_agent_sdk.middleware.base import Middleware, RequestContext, ResponseContext

logger = logging.getLogger(__name__)


class RateLimitMiddleware(Middleware):
    def __init__(
        self,
        max_requests: int = 100,
        window_seconds: float = 60.0,
    ) -> None:
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._request_timestamps: deque[float] = deque()

    def _clean_old_requests(self) -> None:
        now = time.monotonic()
        while (
            self._request_timestamps
            and (now - self._request_timestamps[0]) > self._window_seconds
        ):
            self._request_timestamps.popleft()

    @property
    def remaining_requests(self) -> int:
        self._clean_old_requests()
        return max(0, self._max_requests - len(self._request_timestamps))

    @property
    def is_rate_limited(self) -> bool:
        return self.remaining_requests <= 0

    def process_request(self, context: RequestContext) -> RequestContext:
        self._clean_old_requests()
        if len(self._request_timestamps) >= self._max_requests:
            wait_time = self._window_seconds - (
                time.monotonic() - self._request_timestamps[0]
            )
            raise RateLimitError(
                f"Client-side rate limit: {self._max_requests} requests per "
                f"{self._window_seconds}s window exceeded",
                retry_after=max(0.0, wait_time),
            )
        self._request_timestamps.append(time.monotonic())
        return context

    def process_response(
        self, context: RequestContext, response: ResponseContext
    ) -> ResponseContext:
        return response
