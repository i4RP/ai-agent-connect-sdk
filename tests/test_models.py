from datetime import datetime, timezone

from ai_agent_sdk.models import (
    AgentIdentityToken,
    AgentProfile,
    AppCapability,
    AppInfo,
    AppRegistration,
    AuthStrategy,
    IdentityVerificationResult,
    PaginatedResponse,
    RateLimitInfo,
)


def test_agent_profile_defaults() -> None:
    profile = AgentProfile(id="1", name="bot")
    assert profile.id == "1"
    assert profile.name == "bot"
    assert profile.description == ""
    assert profile.karma == 0
    assert profile.is_verified is False
    assert profile.metadata == {}


def test_agent_profile_full() -> None:
    profile = AgentProfile(
        id="abc",
        name="TestBot",
        description="A test bot",
        avatar_url="https://example.com/avatar.png",
        karma=100,
        is_verified=True,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        metadata={"key": "value"},
    )
    assert profile.karma == 100
    assert profile.is_verified is True
    assert profile.metadata["key"] == "value"


def test_identity_token() -> None:
    token = AgentIdentityToken(
        token="eyJhbG...",
        agent_id="agent-1",
        expires_at=datetime(2026, 1, 1, 1, 0, 0, tzinfo=timezone.utc),
        scopes=["read", "write"],
    )
    assert token.token == "eyJhbG..."
    assert token.scopes == ["read", "write"]


def test_identity_verification_result_valid() -> None:
    result = IdentityVerificationResult(
        valid=True,
        agent=AgentProfile(id="1", name="bot"),
    )
    assert result.valid is True
    assert result.agent is not None
    assert result.agent.name == "bot"


def test_identity_verification_result_invalid() -> None:
    result = IdentityVerificationResult(valid=False, error="Token expired")
    assert result.valid is False
    assert result.error == "Token expired"
    assert result.agent is None


def test_app_capability() -> None:
    cap = AppCapability(
        name="search",
        description="Search for items",
        endpoint="/search",
        method="GET",
        parameters={"q": "string"},
        required_scopes=["read"],
    )
    assert cap.name == "search"
    assert cap.method == "GET"


def test_app_registration() -> None:
    reg = AppRegistration(
        app_id="app-1",
        name="MyApp",
        description="Test app",
        base_url="https://api.example.com",
        capabilities=[
            AppCapability(name="greet", endpoint="/greet"),
        ],
        auth_strategy=AuthStrategy.BEARER,
    )
    assert reg.app_id == "app-1"
    assert len(reg.capabilities) == 1


def test_app_info() -> None:
    info = AppInfo(
        app_id="app-1",
        name="MyApp",
        agent_count=42,
    )
    assert info.agent_count == 42


def test_rate_limit_info() -> None:
    info = RateLimitInfo(limit=100, remaining=50)
    assert info.limit == 100
    assert info.remaining == 50


def test_paginated_response() -> None:
    resp = PaginatedResponse(
        items=[{"id": 1}, {"id": 2}],
        total=10,
        page=1,
        per_page=2,
        has_next=True,
    )
    assert len(resp.items) == 2
    assert resp.has_next is True


def test_auth_strategy_values() -> None:
    assert AuthStrategy.BEARER == "bearer"
    assert AuthStrategy.HEADER == "header"
    assert AuthStrategy.QUERY == "query"
