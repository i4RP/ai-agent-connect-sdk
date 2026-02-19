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

MOLTBOOK_BASE_URL = "https://www.moltbook.com/api/v1"


class MoltbookProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "moltbook"

    @property
    def base_url(self) -> str:
        return MOLTBOOK_BASE_URL

    @property
    def default_auth_strategy(self) -> AuthStrategy:
        return AuthStrategy.BEARER

    @property
    def identity_token_endpoint(self) -> str:
        return "/agents/me/identity-token"

    @property
    def verify_identity_endpoint(self) -> str:
        return "/agents/verify-identity"

    def build_auth_headers(self, api_key: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {api_key}"}

    def build_app_auth_headers(self, app_key: str) -> dict[str, str]:
        return {"X-Moltbook-App-Key": app_key}

    def parse_agent_profile(self, data: dict[str, Any]) -> AgentProfile:
        agent_data = data.get("agent", data)
        created_at = agent_data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        stats = agent_data.get("stats", {})
        return AgentProfile(
            id=agent_data.get("id", ""),
            name=agent_data.get("name", ""),
            description=agent_data.get("description", ""),
            avatar_url=agent_data.get("avatar_url", ""),
            karma=agent_data.get("karma", 0),
            is_verified=agent_data.get("is_claimed", False),
            created_at=created_at,
            metadata={
                "follower_count": agent_data.get("follower_count", 0),
                "posts": stats.get("posts", 0),
                "comments": stats.get("comments", 0),
                "owner": agent_data.get("owner"),
            },
        )

    def parse_identity_token(self, data: dict[str, Any]) -> AgentIdentityToken:
        return AgentIdentityToken(
            token=data.get("token", ""),
            agent_id=data.get("agent_id", ""),
            expires_at=datetime.fromisoformat(
                data.get("expires_at", datetime.now(tz=timezone.utc).isoformat())
            ),
            scopes=data.get("scopes", []),
        )

    def parse_verification_result(self, data: dict[str, Any]) -> IdentityVerificationResult:
        valid = data.get("valid", False)
        agent = None
        if valid and "agent" in data:
            agent = self.parse_agent_profile(data)
        error = data.get("error")
        return IdentityVerificationResult(valid=valid, agent=agent, error=error)
