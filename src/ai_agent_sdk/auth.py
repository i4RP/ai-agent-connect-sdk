from __future__ import annotations

from typing import Any

from ai_agent_sdk.config import SDKConfig
from ai_agent_sdk.exceptions import AuthenticationError
from ai_agent_sdk.models import (
    AgentIdentityToken,
    AgentProfile,
    AuthStrategy,
    IdentityVerificationResult,
)
from ai_agent_sdk.transport import AsyncTransport, Transport


class AuthManager:
    def __init__(self, transport: Transport, config: SDKConfig) -> None:
        self._transport = transport
        self._config = config

    def generate_identity_token(self, scopes: list[str] | None = None) -> AgentIdentityToken:
        payload: dict[str, Any] = {}
        if scopes:
            payload["scopes"] = scopes
        response = self._transport.post("/agents/me/identity-token", json=payload)
        return AgentIdentityToken.model_validate(response.json())

    def verify_identity(self, token: str) -> IdentityVerificationResult:
        if not self._config.app_key:
            raise AuthenticationError("App key is required for identity verification")
        response = self._transport.post(
            "/agents/verify-identity",
            json={"token": token},
            headers={"X-App-Key": self._config.app_key},
        )
        return IdentityVerificationResult.model_validate(response.json())

    def get_current_agent(self) -> AgentProfile:
        response = self._transport.get("/agents/me")
        return AgentProfile.model_validate(response.json())

    def build_auth_headers(
        self,
        token: str,
        strategy: AuthStrategy = AuthStrategy.BEARER,
        header_name: str = "Authorization",
    ) -> dict[str, str]:
        if strategy == AuthStrategy.BEARER:
            return {header_name: f"Bearer {token}"}
        if strategy == AuthStrategy.HEADER:
            return {header_name: token}
        return {}

    def build_auth_params(
        self,
        token: str,
        strategy: AuthStrategy = AuthStrategy.QUERY,
        param_name: str = "api_key",
    ) -> dict[str, str]:
        if strategy == AuthStrategy.QUERY:
            return {param_name: token}
        return {}


class AsyncAuthManager:
    def __init__(self, transport: AsyncTransport, config: SDKConfig) -> None:
        self._transport = transport
        self._config = config

    async def generate_identity_token(
        self, scopes: list[str] | None = None
    ) -> AgentIdentityToken:
        payload: dict[str, Any] = {}
        if scopes:
            payload["scopes"] = scopes
        response = await self._transport.post("/agents/me/identity-token", json=payload)
        return AgentIdentityToken.model_validate(response.json())

    async def verify_identity(self, token: str) -> IdentityVerificationResult:
        if not self._config.app_key:
            raise AuthenticationError("App key is required for identity verification")
        response = await self._transport.post(
            "/agents/verify-identity",
            json={"token": token},
            headers={"X-App-Key": self._config.app_key},
        )
        return IdentityVerificationResult.model_validate(response.json())

    async def get_current_agent(self) -> AgentProfile:
        response = await self._transport.get("/agents/me")
        return AgentProfile.model_validate(response.json())

    def build_auth_headers(
        self,
        token: str,
        strategy: AuthStrategy = AuthStrategy.BEARER,
        header_name: str = "Authorization",
    ) -> dict[str, str]:
        if strategy == AuthStrategy.BEARER:
            return {header_name: f"Bearer {token}"}
        if strategy == AuthStrategy.HEADER:
            return {header_name: token}
        return {}

    def build_auth_params(
        self,
        token: str,
        strategy: AuthStrategy = AuthStrategy.QUERY,
        param_name: str = "api_key",
    ) -> dict[str, str]:
        if strategy == AuthStrategy.QUERY:
            return {param_name: token}
        return {}
