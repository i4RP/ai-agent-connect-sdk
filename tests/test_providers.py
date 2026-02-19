from ai_agent_sdk.models import AuthStrategy
from ai_agent_sdk.providers.custom import CustomProvider
from ai_agent_sdk.providers.moltbook import MoltbookProvider


def test_moltbook_provider_name() -> None:
    provider = MoltbookProvider()
    assert provider.name == "moltbook"
    assert "moltbook.com" in provider.base_url


def test_moltbook_auth_headers() -> None:
    provider = MoltbookProvider()
    headers = provider.build_auth_headers("moltbook_xxx")
    assert headers["Authorization"] == "Bearer moltbook_xxx"


def test_moltbook_app_auth_headers() -> None:
    provider = MoltbookProvider()
    headers = provider.build_app_auth_headers("moltdev_xxx")
    assert headers["X-Moltbook-App-Key"] == "moltdev_xxx"


def test_moltbook_parse_agent_profile() -> None:
    provider = MoltbookProvider()
    data = {
        "agent": {
            "id": "uuid-1",
            "name": "TestBot",
            "description": "A test bot",
            "karma": 100,
            "avatar_url": "https://example.com/avatar.png",
            "is_claimed": True,
            "follower_count": 42,
            "stats": {"posts": 10, "comments": 20},
        }
    }
    profile = provider.parse_agent_profile(data)
    assert profile.id == "uuid-1"
    assert profile.name == "TestBot"
    assert profile.karma == 100
    assert profile.is_verified is True
    assert profile.metadata["follower_count"] == 42


def test_moltbook_parse_verification_result_valid() -> None:
    provider = MoltbookProvider()
    data = {
        "valid": True,
        "agent": {
            "id": "uuid-1",
            "name": "TestBot",
            "description": "",
            "karma": 50,
        },
    }
    result = provider.parse_verification_result(data)
    assert result.valid is True
    assert result.agent is not None
    assert result.agent.name == "TestBot"


def test_moltbook_parse_verification_result_invalid() -> None:
    provider = MoltbookProvider()
    data = {"valid": False, "error": "Token expired"}
    result = provider.parse_verification_result(data)
    assert result.valid is False
    assert result.agent is None
    assert result.error == "Token expired"


def test_custom_provider_basic() -> None:
    provider = CustomProvider(
        provider_name="myplatform",
        provider_base_url="https://api.myplatform.com/v1",
    )
    assert provider.name == "myplatform"
    assert provider.base_url == "https://api.myplatform.com/v1"


def test_custom_provider_auth_headers_bearer() -> None:
    provider = CustomProvider(
        provider_name="test",
        provider_base_url="https://api.test.com",
        auth_strategy=AuthStrategy.BEARER,
    )
    headers = provider.build_auth_headers("my-key")
    assert headers["Authorization"] == "Bearer my-key"


def test_custom_provider_auth_headers_plain() -> None:
    provider = CustomProvider(
        provider_name="test",
        provider_base_url="https://api.test.com",
        auth_strategy=AuthStrategy.HEADER,
        auth_header="X-API-Key",
    )
    headers = provider.build_auth_headers("my-key")
    assert headers["X-API-Key"] == "my-key"


def test_custom_provider_configurable_endpoints() -> None:
    provider = CustomProvider(
        provider_name="test",
        provider_base_url="https://api.test.com",
        identity_token_path="/auth/token",
        verify_identity_path="/auth/verify",
        agent_profile_path="/me",
    )
    assert provider.identity_token_endpoint == "/auth/token"
    assert provider.verify_identity_endpoint == "/auth/verify"
    assert provider.agent_profile_endpoint == "/me"


def test_custom_provider_parse_agent_profile() -> None:
    provider = CustomProvider(
        provider_name="test",
        provider_base_url="https://api.test.com",
    )
    data = {"id": "agent-1", "name": "Bot", "description": "test"}
    profile = provider.parse_agent_profile(data)
    assert profile.id == "agent-1"
    assert profile.name == "Bot"


def test_custom_provider_parse_verification_result() -> None:
    provider = CustomProvider(
        provider_name="test",
        provider_base_url="https://api.test.com",
    )
    data = {
        "valid": True,
        "agent": {"id": "1", "name": "Bot"},
    }
    result = provider.parse_verification_result(data)
    assert result.valid is True
    assert result.agent is not None
