import os

from ai_agent_sdk.config import SDKConfig


def test_default_config() -> None:
    config = SDKConfig()
    assert config.api_key == ""
    assert config.timeout == 30.0
    assert config.retries == 3
    assert config.rate_limit_enabled is True
    assert config.provider == "generic"


def test_custom_config() -> None:
    config = SDKConfig(
        api_key="test-key",
        app_key="app-key",
        base_url="https://api.example.com",
        timeout=10.0,
        retries=5,
        provider="moltbook",
    )
    assert config.api_key == "test-key"
    assert config.app_key == "app-key"
    assert config.base_url == "https://api.example.com"
    assert config.timeout == 10.0
    assert config.retries == 5
    assert config.provider == "moltbook"


def test_config_from_env(monkeypatch: object) -> None:
    os.environ["AGENT_SDK_API_KEY"] = "env-key"
    os.environ["AGENT_SDK_BASE_URL"] = "https://env.example.com"
    os.environ["AGENT_SDK_TIMEOUT"] = "15.0"
    os.environ["AGENT_SDK_PROVIDER"] = "moltbook"
    try:
        config = SDKConfig.from_env()
        assert config.api_key == "env-key"
        assert config.base_url == "https://env.example.com"
        assert config.timeout == 15.0
        assert config.provider == "moltbook"
    finally:
        del os.environ["AGENT_SDK_API_KEY"]
        del os.environ["AGENT_SDK_BASE_URL"]
        del os.environ["AGENT_SDK_TIMEOUT"]
        del os.environ["AGENT_SDK_PROVIDER"]


def test_config_from_env_custom_prefix() -> None:
    os.environ["MYAPP_API_KEY"] = "custom-key"
    try:
        config = SDKConfig.from_env(prefix="MYAPP")
        assert config.api_key == "custom-key"
    finally:
        del os.environ["MYAPP_API_KEY"]
