from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ai_agent_sdk.models import (
    AgentIdentityToken,
    AgentProfile,
    AuthStrategy,
    IdentityVerificationResult,
)
from ai_agent_sdk.providers.base import BaseProvider


class CustomProvider(BaseProvider):
    def __init__(
        self,
        provider_name: str,
        provider_base_url: str,
        auth_strategy: AuthStrategy = AuthStrategy.BEARER,
        auth_header: str = "Authorization",
        app_auth_header: str = "X-App-Key",
        identity_token_path: str = "/agents/me/identity-token",
        verify_identity_path: str = "/agents/verify-identity",
        agent_profile_path: str = "/agents/me",
        app_register_path: str = "/apps/register",
        app_list_path: str = "/apps",
    ) -> None:
        self._name = provider_name
        self._base_url = provider_base_url
        self._auth_strategy = auth_strategy
        self._auth_header = auth_header
        self._app_auth_header = app_auth_header
        self._identity_token_path = identity_token_path
        self._verify_identity_path = verify_identity_path
        self._agent_profile_path = agent_profile_path
        self._app_register_path = app_register_path
        self._app_list_path = app_list_path

    @property
    def name(self) -> str:
        return self._name

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def default_auth_strategy(self) -> AuthStrategy:
        return self._auth_strategy

    @property
    def identity_token_endpoint(self) -> str:
        return self._identity_token_path

    @property
    def verify_identity_endpoint(self) -> str:
        return self._verify_identity_path

    @property
    def agent_profile_endpoint(self) -> str:
        return self._agent_profile_path

    @property
    def app_register_endpoint(self) -> str:
        return self._app_register_path

    @property
    def app_list_endpoint(self) -> str:
        return self._app_list_path

    def build_auth_headers(self, api_key: str) -> dict[str, str]:
        if self._auth_strategy == AuthStrategy.BEARER:
            return {self._auth_header: f"Bearer {api_key}"}
        return {self._auth_header: api_key}

    def build_app_auth_headers(self, app_key: str) -> dict[str, str]:
        return {self._app_auth_header: app_key}

    def parse_agent_profile(self, data: dict[str, Any]) -> AgentProfile:
        return AgentProfile.model_validate(data)

    def parse_identity_token(self, data: dict[str, Any]) -> AgentIdentityToken:
        expires_at = data.get("expires_at")
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        elif expires_at is None:
            expires_at = datetime.now(tz=timezone.utc)
        return AgentIdentityToken(
            token=data.get("token", ""),
            agent_id=data.get("agent_id", ""),
            expires_at=expires_at,
            scopes=data.get("scopes", []),
        )

    def parse_verification_result(self, data: dict[str, Any]) -> IdentityVerificationResult:
        valid = data.get("valid", False)
        agent = None
        if valid and "agent" in data:
            agent = self.parse_agent_profile(data["agent"])
        return IdentityVerificationResult(
            valid=valid,
            agent=agent,
            error=data.get("error"),
        )
