from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ai_agent_sdk.models import (
    AgentIdentityToken,
    AgentProfile,
    AppCapability,
    AppInfo,
    AppRegistration,
    AuthStrategy,
    IdentityVerificationResult,
    PaginatedResponse,
)


class BaseProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def base_url(self) -> str:
        ...

    @property
    def default_auth_strategy(self) -> AuthStrategy:
        return AuthStrategy.BEARER

    @property
    def identity_token_endpoint(self) -> str:
        return "/agents/me/identity-token"

    @property
    def verify_identity_endpoint(self) -> str:
        return "/agents/verify-identity"

    @property
    def agent_profile_endpoint(self) -> str:
        return "/agents/me"

    @property
    def app_register_endpoint(self) -> str:
        return "/apps/register"

    @property
    def app_list_endpoint(self) -> str:
        return "/apps"

    @property
    def app_detail_endpoint(self) -> str:
        return "/apps/{app_id}"

    @abstractmethod
    def build_auth_headers(self, api_key: str) -> dict[str, str]:
        ...

    @abstractmethod
    def build_app_auth_headers(self, app_key: str) -> dict[str, str]:
        ...

    @abstractmethod
    def parse_agent_profile(self, data: dict[str, Any]) -> AgentProfile:
        ...

    @abstractmethod
    def parse_identity_token(self, data: dict[str, Any]) -> AgentIdentityToken:
        ...

    @abstractmethod
    def parse_verification_result(self, data: dict[str, Any]) -> IdentityVerificationResult:
        ...

    def parse_app_registration(self, data: dict[str, Any]) -> AppRegistration:
        return AppRegistration.model_validate(data)

    def parse_app_info(self, data: dict[str, Any]) -> AppInfo:
        return AppInfo.model_validate(data)

    def parse_app_list(self, data: dict[str, Any]) -> PaginatedResponse:
        return PaginatedResponse.model_validate(data)

    def format_register_payload(
        self,
        name: str,
        description: str,
        base_url: str,
        capabilities: list[AppCapability],
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": name,
            "description": description,
            "base_url": base_url,
            "capabilities": [cap.model_dump() for cap in capabilities],
        }
        if metadata:
            payload["metadata"] = metadata
        return payload
