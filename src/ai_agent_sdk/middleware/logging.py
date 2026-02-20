from __future__ import annotations

import logging
import time

from ai_agent_sdk.middleware.base import Middleware, RequestContext, ResponseContext

logger = logging.getLogger(__name__)


class LoggingMiddleware(Middleware):
    def __init__(self, log_level: int = logging.INFO) -> None:
        self._log_level = log_level

    def process_request(self, context: RequestContext) -> RequestContext:
        context.metadata["_request_start"] = time.monotonic()
        logger.log(
            self._log_level,
            "-> %s %s",
            context.method,
            context.path,
        )
        return context

    def process_response(
        self, context: RequestContext, response: ResponseContext
    ) -> ResponseContext:
        start = context.metadata.get("_request_start")
        duration_ms = (time.monotonic() - start) * 1000 if start else 0
        logger.log(
            self._log_level,
            "<- %s %s [%d] (%.1fms)",
            context.method,
            context.path,
            response.status_code,
            duration_ms,
        )
        return response
