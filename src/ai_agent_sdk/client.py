from __future__ import annotations

from typing import Any

from ai_agent_sdk.auth import AsyncAuthManager, AuthManager
from ai_agent_sdk.config import SDKConfig
from ai_agent_sdk.exceptions import ConfigurationError
from ai_agent_sdk.models import (
    AgentIdentityToken,
    AgentProfile,
    AppCapability,
    AppInfo,
    AppRegistration,
    IdentityVerificationResult,
    PaginatedResponse,
    RateLimitInfo,
)
from ai_agent_sdk.providers.base import BaseProvider
from ai_agent_sdk.providers.custom import CustomProvider
from ai_agent_sdk.providers.moltbook import MoltbookProvider
from ai_agent_sdk.registry import AppRegistry, AsyncAppRegistry
from ai_agent_sdk.transport import AsyncTransport, Transport
from ai_agent_sdk.utils.helpers import sanitize_url

PROVIDER_REGISTRY: dict[str, type[BaseProvider]] = {
    "moltbook": MoltbookProvider,
}


def _resolve_provider(
    provider: BaseProvider | str | None,
    base_url: str,
) -> BaseProvider:
    if isinstance(provider, BaseProvider):
        return provider
    if isinstance(provider, str):
        if provider in PROVIDER_REGISTRY:
            return PROVIDER_REGISTRY[provider]()
        return CustomProvider(
            provider_name=provider,
            provider_base_url=sanitize_url(base_url) if base_url else "",
        )
    if base_url:
        return CustomProvider(
            provider_name="custom",
            provider_base_url=sanitize_url(base_url),
        )
    raise ConfigurationError(
        "Either a provider or base_url must be specified"
    )


class AgentConnectClient:
    def __init__(
        self,
        api_key: str = "",
        app_key: str = "",
        base_url: str = "",
        provider: BaseProvider | str | None = None,
        timeout: float = 30.0,
        retries: int = 3,
        retry_delay: float = 1.0,
        custom_headers: dict[str, str] | None = None,
        config: SDKConfig | None = None,
    ) -> None:
        if config is not None:
            self._config = config
        else:
            self._config = SDKConfig(
                api_key=api_key,
                app_key=app_key,
                base_url=base_url,
                timeout=timeout,
                retries=retries,
                retry_delay=retry_delay,
                custom_headers=custom_headers or {},
            )

        self._provider = _resolve_provider(provider, self._config.base_url)

        if not self._config.base_url:
            self._config.base_url = self._provider.base_url

        auth_headers = self._provider.build_auth_headers(self._config.api_key)
        merged_headers = {**self._config.custom_headers, **auth_headers}
        self._config.custom_headers = merged_headers

        self._transport = Transport(self._config)
        self._auth = AuthManager(self._transport, self._config)
        self._apps = AppRegistry(self._transport, self._provider)

    @classmethod
    def from_env(cls, prefix: str = "AGENT_SDK") -> AgentConnectClient:
        config = SDKConfig.from_env(prefix)
        return cls(config=config, provider=config.provider)

    @property
    def provider(self) -> BaseProvider:
        return self._provider

    @property
    def auth(self) -> AuthManager:
        return self._auth

    @property
    def apps(self) -> AppRegistry:
        return self._apps

    @property
    def transport(self) -> Transport:
        return self._transport

    def get_rate_limit_info(self) -> RateLimitInfo | None:
        return self._transport.last_rate_limit

    def generate_identity_token(
        self, scopes: list[str] | None = None
    ) -> AgentIdentityToken:
        payload: dict[str, Any] = {}
        if scopes:
            payload["scopes"] = scopes
        response = self._transport.post(
            self._provider.identity_token_endpoint, json=payload
        )
        return self._provider.parse_identity_token(response.json())

    def verify_identity(self, token: str) -> IdentityVerificationResult:
        app_headers = self._provider.build_app_auth_headers(self._config.app_key)
        response = self._transport.post(
            self._provider.verify_identity_endpoint,
            json={"token": token},
            headers=app_headers,
        )
        return self._provider.parse_verification_result(response.json())

    def get_agent_profile(self) -> AgentProfile:
        response = self._transport.get(self._provider.agent_profile_endpoint)
        return self._provider.parse_agent_profile(response.json())

    def register_app(
        self,
        name: str,
        description: str = "",
        base_url: str = "",
        capabilities: list[AppCapability] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AppRegistration:
        return self._apps.register(
            name=name,
            description=description,
            base_url=base_url,
            capabilities=capabilities,
            metadata=metadata,
        )

    def get_app(self, app_id: str) -> AppInfo:
        return self._apps.get(app_id)

    def list_apps(
        self,
        page: int = 1,
        per_page: int = 25,
        sort: str = "popular",
    ) -> PaginatedResponse:
        return self._apps.list(page=page, per_page=per_page, sort=sort)

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        response = self._transport.request(
            method, path, json=json, params=params, headers=headers
        )
        return response.json()

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> AgentConnectClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncAgentConnectClient:
    def __init__(
        self,
        api_key: str = "",
        app_key: str = "",
        base_url: str = "",
        provider: BaseProvider | str | None = None,
        timeout: float = 30.0,
        retries: int = 3,
        retry_delay: float = 1.0,
        custom_headers: dict[str, str] | None = None,
        config: SDKConfig | None = None,
    ) -> None:
        if config is not None:
            self._config = config
        else:
            self._config = SDKConfig(
                api_key=api_key,
                app_key=app_key,
                base_url=base_url,
                timeout=timeout,
                retries=retries,
                retry_delay=retry_delay,
                custom_headers=custom_headers or {},
            )

        self._provider = _resolve_provider(provider, self._config.base_url)

        if not self._config.base_url:
            self._config.base_url = self._provider.base_url

        auth_headers = self._provider.build_auth_headers(self._config.api_key)
        merged_headers = {**self._config.custom_headers, **auth_headers}
        self._config.custom_headers = merged_headers

        self._transport = AsyncTransport(self._config)
        self._auth = AsyncAuthManager(self._transport, self._config)
        self._apps = AsyncAppRegistry(self._transport, self._provider)

    @classmethod
    def from_env(cls, prefix: str = "AGENT_SDK") -> AsyncAgentConnectClient:
        config = SDKConfig.from_env(prefix)
        return cls(config=config, provider=config.provider)

    @property
    def provider(self) -> BaseProvider:
        return self._provider

    @property
    def auth(self) -> AsyncAuthManager:
        return self._auth

    @property
    def apps(self) -> AsyncAppRegistry:
        return self._apps

    @property
    def transport(self) -> AsyncTransport:
        return self._transport

    def get_rate_limit_info(self) -> RateLimitInfo | None:
        return self._transport.last_rate_limit

    async def generate_identity_token(
        self, scopes: list[str] | None = None
    ) -> AgentIdentityToken:
        payload: dict[str, Any] = {}
        if scopes:
            payload["scopes"] = scopes
        response = await self._transport.post(
            self._provider.identity_token_endpoint, json=payload
        )
        return self._provider.parse_identity_token(response.json())

    async def verify_identity(self, token: str) -> IdentityVerificationResult:
        app_headers = self._provider.build_app_auth_headers(self._config.app_key)
        response = await self._transport.post(
            self._provider.verify_identity_endpoint,
            json={"token": token},
            headers=app_headers,
        )
        return self._provider.parse_verification_result(response.json())

    async def get_agent_profile(self) -> AgentProfile:
        response = await self._transport.get(self._provider.agent_profile_endpoint)
        return self._provider.parse_agent_profile(response.json())

    async def register_app(
        self,
        name: str,
        description: str = "",
        base_url: str = "",
        capabilities: list[AppCapability] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AppRegistration:
        return await self._apps.register(
            name=name,
            description=description,
            base_url=base_url,
            capabilities=capabilities,
            metadata=metadata,
        )

    async def get_app(self, app_id: str) -> AppInfo:
        return await self._apps.get(app_id)

    async def list_apps(
        self,
        page: int = 1,
        per_page: int = 25,
        sort: str = "popular",
    ) -> PaginatedResponse:
        return await self._apps.list(page=page, per_page=per_page, sort=sort)

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        response = await self._transport.request(
            method, path, json=json, params=params, headers=headers
        )
        return response.json()

    async def close(self) -> None:
        await self._transport.close()

    async def __aenter__(self) -> AsyncAgentConnectClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
