from __future__ import annotations

import contextlib
import logging
import time

from ai_agent_sdk.middleware.base import Middleware, RequestContext, ResponseContext

logger = logging.getLogger(__name__)

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class RetryMiddleware(Middleware):
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
    ) -> None:
        self._max_retries = max_retries
        self._base_delay = base_delay
        self._max_delay = max_delay
        self._backoff_factor = backoff_factor

    def process_request(self, context: RequestContext) -> RequestContext:
        context.metadata["retry_count"] = 0
        context.metadata["max_retries"] = self._max_retries
        return context

    def process_response(
        self, context: RequestContext, response: ResponseContext
    ) -> ResponseContext:
        retry_count = context.metadata.get("retry_count", 0)
        if response.status_code in RETRYABLE_STATUS_CODES and retry_count < self._max_retries:
            delay = min(
                self._base_delay * (self._backoff_factor**retry_count),
                self._max_delay,
            )
            retry_after = response.headers.get("Retry-After")
            if retry_after is not None:
                with contextlib.suppress(ValueError):
                    delay = float(retry_after)
            logger.warning(
                "Retryable status %d on %s %s (attempt %d/%d), waiting %.1fs",
                response.status_code,
                context.method,
                context.path,
                retry_count + 1,
                self._max_retries,
                delay,
            )
            context.metadata["retry_count"] = retry_count + 1
            context.metadata["retry_delay"] = delay
            response.metadata["should_retry"] = True
            response.metadata["retry_delay"] = delay
        return response

    @staticmethod
    def should_retry(response: ResponseContext) -> bool:
        return bool(response.metadata.get("should_retry", False))

    @staticmethod
    def get_retry_delay(response: ResponseContext) -> float:
        return float(response.metadata.get("retry_delay", 1.0))

    @staticmethod
    def wait_for_retry(response: ResponseContext) -> None:
        if RetryMiddleware.should_retry(response):
            time.sleep(RetryMiddleware.get_retry_delay(response))
