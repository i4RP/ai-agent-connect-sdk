import pytest

from ai_agent_sdk.client import AgentConnectClient, AsyncAgentConnectClient
from ai_agent_sdk.config import SDKConfig
from ai_agent_sdk.exceptions import ConfigurationError
from ai_agent_sdk.providers.custom import CustomProvider
from ai_agent_sdk.providers.moltbook import MoltbookProvider


def test_client_with_moltbook_provider() -> None:
    client = AgentConnectClient(
        api_key="moltbook_xxx",
        provider="moltbook",
    )
    assert isinstance(client.provider, MoltbookProvider)
    assert client.provider.name == "moltbook"
    client.close()


def test_client_with_custom_provider() -> None:
    provider = CustomProvider(
        provider_name="myplatform",
        provider_base_url="https://api.example.com/v1",
    )
    client = AgentConnectClient(
        api_key="test-key",
        provider=provider,
    )
    assert client.provider.name == "myplatform"
    client.close()


def test_client_with_base_url() -> None:
    client = AgentConnectClient(
        api_key="test-key",
        base_url="https://api.example.com",
    )
    assert client.provider.name == "custom"
    client.close()


def test_client_requires_provider_or_url() -> None:
    with pytest.raises(ConfigurationError):
        AgentConnectClient(api_key="test-key")


def test_client_context_manager() -> None:
    with AgentConnectClient(
        api_key="test-key",
        base_url="https://api.example.com",
    ) as client:
        assert client.provider is not None


def test_client_from_config() -> None:
    config = SDKConfig(
        api_key="cfg-key",
        base_url="https://api.example.com",
    )
    client = AgentConnectClient(config=config, provider="moltbook")
    assert isinstance(client.provider, MoltbookProvider)
    client.close()


def test_client_provider_string_unknown() -> None:
    client = AgentConnectClient(
        api_key="test-key",
        provider="unknown_platform",
        base_url="https://api.unknown.com",
    )
    assert client.provider.name == "unknown_platform"
    client.close()


def test_client_has_auth_property() -> None:
    client = AgentConnectClient(
        api_key="test-key",
        base_url="https://api.example.com",
    )
    assert client.auth is not None
    client.close()


def test_client_has_apps_property() -> None:
    client = AgentConnectClient(
        api_key="test-key",
        base_url="https://api.example.com",
    )
    assert client.apps is not None
    client.close()


def test_client_rate_limit_info_initially_none() -> None:
    client = AgentConnectClient(
        api_key="test-key",
        base_url="https://api.example.com",
    )
    assert client.get_rate_limit_info() is None
    client.close()


def test_async_client_with_moltbook() -> None:
    client = AsyncAgentConnectClient(
        api_key="moltbook_xxx",
        provider="moltbook",
    )
    assert isinstance(client.provider, MoltbookProvider)


def test_async_client_with_base_url() -> None:
    client = AsyncAgentConnectClient(
        api_key="test-key",
        base_url="https://api.example.com",
    )
    assert client.provider.name == "custom"
