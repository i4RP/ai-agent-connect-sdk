from __future__ import annotations

import logging
from typing import Any

import httpx

from ai_agent_sdk.config import SDKConfig
from ai_agent_sdk.exceptions import TransportError, raise_for_status
from ai_agent_sdk.models import RateLimitInfo

logger = logging.getLogger(__name__)


class Transport:
    def __init__(self, config: SDKConfig) -> None:
        self._config = config
        self._client: httpx.Client | None = None
        self._last_rate_limit: RateLimitInfo | None = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None or self._client.is_closed:
            headers = dict(self._config.custom_headers)
            if self._config.api_key:
                headers["Authorization"] = f"Bearer {self._config.api_key}"
            self._client = httpx.Client(
                base_url=self._config.base_url,
                headers=headers,
                timeout=httpx.Timeout(self._config.timeout),
            )
        return self._client

    @property
    def last_rate_limit(self) -> RateLimitInfo | None:
        return self._last_rate_limit

    def _parse_rate_limit(self, response: httpx.Response) -> RateLimitInfo | None:
        limit = response.headers.get("X-RateLimit-Limit")
        remaining = response.headers.get("X-RateLimit-Remaining")
        if limit is not None and remaining is not None:
            info = RateLimitInfo(limit=int(limit), remaining=int(remaining))
            self._last_rate_limit = info
            return info
        return None

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        try:
            if self._config.log_requests:
                logger.info("Request: %s %s params=%s", method, path, params)
            response = self.client.request(
                method,
                path,
                json=json,
                params=params,
                headers=headers,
            )
            self._parse_rate_limit(response)
            if self._config.log_responses:
                logger.info("Response: %s %s", response.status_code, response.text[:500])
            raise_for_status(response.status_code, response.text)
            return response
        except httpx.HTTPError as exc:
            raise TransportError(str(exc)) from exc

    def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        return self.request("GET", path, params=params, headers=headers)

    def post(
        self,
        path: str,
        *,
        json: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        return self.request("POST", path, json=json, headers=headers)

    def put(
        self,
        path: str,
        *,
        json: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        return self.request("PUT", path, json=json, headers=headers)

    def delete(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        return self.request("DELETE", path, headers=headers)

    def close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            self._client.close()
            self._client = None


class AsyncTransport:
    def __init__(self, config: SDKConfig) -> None:
        self._config = config
        self._client: httpx.AsyncClient | None = None
        self._last_rate_limit: RateLimitInfo | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            headers = dict(self._config.custom_headers)
            if self._config.api_key:
                headers["Authorization"] = f"Bearer {self._config.api_key}"
            self._client = httpx.AsyncClient(
                base_url=self._config.base_url,
                headers=headers,
                timeout=httpx.Timeout(self._config.timeout),
            )
        return self._client

    @property
    def last_rate_limit(self) -> RateLimitInfo | None:
        return self._last_rate_limit

    def _parse_rate_limit(self, response: httpx.Response) -> RateLimitInfo | None:
        limit = response.headers.get("X-RateLimit-Limit")
        remaining = response.headers.get("X-RateLimit-Remaining")
        if limit is not None and remaining is not None:
            info = RateLimitInfo(limit=int(limit), remaining=int(remaining))
            self._last_rate_limit = info
            return info
        return None

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        try:
            if self._config.log_requests:
                logger.info("Request: %s %s params=%s", method, path, params)
            response = await self.client.request(
                method,
                path,
                json=json,
                params=params,
                headers=headers,
            )
            self._parse_rate_limit(response)
            if self._config.log_responses:
                logger.info("Response: %s %s", response.status_code, response.text[:500])
            raise_for_status(response.status_code, response.text)
            return response
        except httpx.HTTPError as exc:
            raise TransportError(str(exc)) from exc

    async def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        return await self.request("GET", path, params=params, headers=headers)

    async def post(
        self,
        path: str,
        *,
        json: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        return await self.request("POST", path, json=json, headers=headers)

    async def put(
        self,
        path: str,
        *,
        json: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        return await self.request("PUT", path, json=json, headers=headers)

    async def delete(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        return await self.request("DELETE", path, headers=headers)

    async def close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
