import pytest

from ai_agent_sdk.middleware.base import (
    Middleware,
    MiddlewarePipeline,
    RequestContext,
    ResponseContext,
)
from ai_agent_sdk.middleware.logging import LoggingMiddleware
from ai_agent_sdk.middleware.rate_limit import RateLimitMiddleware
from ai_agent_sdk.middleware.retry import RetryMiddleware


class TrackingMiddleware(Middleware):
    def __init__(self) -> None:
        self.request_count = 0
        self.response_count = 0

    def process_request(self, context: RequestContext) -> RequestContext:
        self.request_count += 1
        return context

    def process_response(
        self, context: RequestContext, response: ResponseContext
    ) -> ResponseContext:
        self.response_count += 1
        return response


def test_middleware_pipeline_order() -> None:
    mw1 = TrackingMiddleware()
    mw2 = TrackingMiddleware()
    pipeline = MiddlewarePipeline()
    pipeline.add(mw1).add(mw2)

    ctx = RequestContext(method="GET", path="/test")
    pipeline.process_request(ctx)
    assert mw1.request_count == 1
    assert mw2.request_count == 1

    resp = ResponseContext(status_code=200)
    pipeline.process_response(ctx, resp)
    assert mw1.response_count == 1
    assert mw2.response_count == 1


def test_middleware_pipeline_wrap() -> None:
    tracker = TrackingMiddleware()
    pipeline = MiddlewarePipeline()
    pipeline.add(tracker)

    def handler(ctx: RequestContext) -> ResponseContext:
        return ResponseContext(status_code=200)

    wrapped = pipeline.wrap(handler)
    ctx = RequestContext(method="GET", path="/test")
    resp = wrapped(ctx)
    assert resp.status_code == 200
    assert tracker.request_count == 1
    assert tracker.response_count == 1


def test_retry_middleware_marks_retryable() -> None:
    mw = RetryMiddleware(max_retries=3)
    ctx = RequestContext(method="GET", path="/test")
    ctx = mw.process_request(ctx)
    assert ctx.metadata["retry_count"] == 0

    resp = ResponseContext(status_code=429, headers={"Retry-After": "2"})
    resp = mw.process_response(ctx, resp)
    assert RetryMiddleware.should_retry(resp) is True
    assert RetryMiddleware.get_retry_delay(resp) == 2.0


def test_retry_middleware_no_retry_on_success() -> None:
    mw = RetryMiddleware(max_retries=3)
    ctx = RequestContext(method="GET", path="/test")
    ctx = mw.process_request(ctx)

    resp = ResponseContext(status_code=200)
    resp = mw.process_response(ctx, resp)
    assert RetryMiddleware.should_retry(resp) is False


def test_retry_middleware_max_retries_exceeded() -> None:
    mw = RetryMiddleware(max_retries=2)
    ctx = RequestContext(method="GET", path="/test")
    ctx = mw.process_request(ctx)
    ctx.metadata["retry_count"] = 2

    resp = ResponseContext(status_code=500)
    resp = mw.process_response(ctx, resp)
    assert RetryMiddleware.should_retry(resp) is False


def test_rate_limit_middleware_allows_requests() -> None:
    mw = RateLimitMiddleware(max_requests=10, window_seconds=60.0)
    ctx = RequestContext(method="GET", path="/test")
    result = mw.process_request(ctx)
    assert result is ctx
    assert mw.remaining_requests == 9


def test_rate_limit_middleware_blocks_when_exceeded() -> None:
    from ai_agent_sdk.exceptions import RateLimitError

    mw = RateLimitMiddleware(max_requests=2, window_seconds=60.0)
    mw.process_request(RequestContext(method="GET", path="/1"))
    mw.process_request(RequestContext(method="GET", path="/2"))

    with pytest.raises(RateLimitError):
        mw.process_request(RequestContext(method="GET", path="/3"))


def test_rate_limit_remaining() -> None:
    mw = RateLimitMiddleware(max_requests=5, window_seconds=60.0)
    assert mw.remaining_requests == 5
    assert mw.is_rate_limited is False

    for i in range(5):
        mw.process_request(RequestContext(method="GET", path=f"/{i}"))

    assert mw.remaining_requests == 0
    assert mw.is_rate_limited is True


def test_logging_middleware_adds_timing() -> None:
    mw = LoggingMiddleware()
    ctx = RequestContext(method="POST", path="/action")
    ctx = mw.process_request(ctx)
    assert "_request_start" in ctx.metadata

    resp = ResponseContext(status_code=201)
    mw.process_response(ctx, resp)
