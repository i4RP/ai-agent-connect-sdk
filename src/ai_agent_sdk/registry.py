from __future__ import annotations

from typing import Any

from ai_agent_sdk.models import (
    AppCapability,
    AppInfo,
    AppRegistration,
    PaginatedResponse,
)
from ai_agent_sdk.providers.base import BaseProvider
from ai_agent_sdk.transport import AsyncTransport, Transport


class AppRegistry:
    def __init__(self, transport: Transport, provider: BaseProvider) -> None:
        self._transport = transport
        self._provider = provider

    def register(
        self,
        name: str,
        description: str = "",
        base_url: str = "",
        capabilities: list[AppCapability] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AppRegistration:
        payload = self._provider.format_register_payload(
            name=name,
            description=description,
            base_url=base_url,
            capabilities=capabilities or [],
            metadata=metadata,
        )
        response = self._transport.post(self._provider.app_register_endpoint, json=payload)
        return self._provider.parse_app_registration(response.json())

    def get(self, app_id: str) -> AppInfo:
        endpoint = self._provider.app_detail_endpoint.format(app_id=app_id)
        response = self._transport.get(endpoint)
        return self._provider.parse_app_info(response.json())

    def list(
        self,
        page: int = 1,
        per_page: int = 25,
        sort: str = "popular",
    ) -> PaginatedResponse:
        params: dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "sort": sort,
        }
        response = self._transport.get(self._provider.app_list_endpoint, params=params)
        return self._provider.parse_app_list(response.json())

    def update(
        self,
        app_id: str,
        name: str | None = None,
        description: str | None = None,
        capabilities: list[AppCapability] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AppInfo:
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if capabilities is not None:
            payload["capabilities"] = [cap.model_dump() for cap in capabilities]
        if metadata is not None:
            payload["metadata"] = metadata
        endpoint = self._provider.app_detail_endpoint.format(app_id=app_id)
        response = self._transport.put(endpoint, json=payload)
        return self._provider.parse_app_info(response.json())

    def delete(self, app_id: str) -> None:
        endpoint = self._provider.app_detail_endpoint.format(app_id=app_id)
        self._transport.delete(endpoint)


class AsyncAppRegistry:
    def __init__(self, transport: AsyncTransport, provider: BaseProvider) -> None:
        self._transport = transport
        self._provider = provider

    async def register(
        self,
        name: str,
        description: str = "",
        base_url: str = "",
        capabilities: list[AppCapability] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AppRegistration:
        payload = self._provider.format_register_payload(
            name=name,
            description=description,
            base_url=base_url,
            capabilities=capabilities or [],
            metadata=metadata,
        )
        response = await self._transport.post(
            self._provider.app_register_endpoint, json=payload
        )
        return self._provider.parse_app_registration(response.json())

    async def get(self, app_id: str) -> AppInfo:
        endpoint = self._provider.app_detail_endpoint.format(app_id=app_id)
        response = await self._transport.get(endpoint)
        return self._provider.parse_app_info(response.json())

    async def list(
        self,
        page: int = 1,
        per_page: int = 25,
        sort: str = "popular",
    ) -> PaginatedResponse:
        params: dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "sort": sort,
        }
        response = await self._transport.get(
            self._provider.app_list_endpoint, params=params
        )
        return self._provider.parse_app_list(response.json())

    async def update(
        self,
        app_id: str,
        name: str | None = None,
        description: str | None = None,
        capabilities: list[AppCapability] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AppInfo:
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if capabilities is not None:
            payload["capabilities"] = [cap.model_dump() for cap in capabilities]
        if metadata is not None:
            payload["metadata"] = metadata
        endpoint = self._provider.app_detail_endpoint.format(app_id=app_id)
        response = await self._transport.put(endpoint, json=payload)
        return self._provider.parse_app_info(response.json())

    async def delete(self, app_id: str) -> None:
        endpoint = self._provider.app_detail_endpoint.format(app_id=app_id)
        await self._transport.delete(endpoint)
