from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RequestContext:
    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, Any] | None = None
    json_body: Any | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResponseContext:
    status_code: int
    body: Any = None
    headers: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class Middleware(ABC):
    @abstractmethod
    def process_request(self, context: RequestContext) -> RequestContext:
        ...

    @abstractmethod
    def process_response(
        self, context: RequestContext, response: ResponseContext
    ) -> ResponseContext:
        ...


class MiddlewarePipeline:
    def __init__(self) -> None:
        self._middlewares: list[Middleware] = []

    def add(self, middleware: Middleware) -> MiddlewarePipeline:
        self._middlewares.append(middleware)
        return self

    def process_request(self, context: RequestContext) -> RequestContext:
        for mw in self._middlewares:
            context = mw.process_request(context)
        return context

    def process_response(
        self, context: RequestContext, response: ResponseContext
    ) -> ResponseContext:
        for mw in reversed(self._middlewares):
            response = mw.process_response(context, response)
        return response

    def wrap(
        self, handler: Callable[[RequestContext], ResponseContext]
    ) -> Callable[[RequestContext], ResponseContext]:
        def wrapped(ctx: RequestContext) -> ResponseContext:
            ctx = self.process_request(ctx)
            resp = handler(ctx)
            return self.process_response(ctx, resp)

        return wrapped
