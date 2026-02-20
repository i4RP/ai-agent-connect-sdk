import pytest

from ai_agent_sdk.exceptions import (
    AgentSDKError,
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    NotFoundError,
    ProviderError,
    RateLimitError,
    TransportError,
    ValidationError,
    raise_for_status,
)


def test_agent_sdk_error() -> None:
    err = AgentSDKError("test error", status_code=500)
    assert err.message == "test error"
    assert err.status_code == 500
    assert str(err) == "test error"


def test_authentication_error() -> None:
    err = AuthenticationError()
    assert err.status_code == 401
    assert "Authentication" in err.message


def test_authorization_error() -> None:
    err = AuthorizationError()
    assert err.status_code == 403


def test_not_found_error() -> None:
    err = NotFoundError()
    assert err.status_code == 404


def test_rate_limit_error() -> None:
    err = RateLimitError(retry_after=30.0)
    assert err.status_code == 429
    assert err.retry_after == 30.0


def test_validation_error() -> None:
    err = ValidationError()
    assert err.status_code == 422


def test_transport_error() -> None:
    err = TransportError("connection failed")
    assert err.message == "connection failed"


def test_provider_error() -> None:
    err = ProviderError("bad provider", provider="moltbook")
    assert err.provider == "moltbook"


def test_configuration_error() -> None:
    err = ConfigurationError("missing key")
    assert "missing key" in err.message


def test_raise_for_status_401() -> None:
    with pytest.raises(AuthenticationError):
        raise_for_status(401, "unauthorized")


def test_raise_for_status_403() -> None:
    with pytest.raises(AuthorizationError):
        raise_for_status(403, "forbidden")


def test_raise_for_status_404() -> None:
    with pytest.raises(NotFoundError):
        raise_for_status(404, "not found")


def test_raise_for_status_422() -> None:
    with pytest.raises(ValidationError):
        raise_for_status(422, "invalid")


def test_raise_for_status_429() -> None:
    with pytest.raises(RateLimitError):
        raise_for_status(429, "too many requests")


def test_raise_for_status_500() -> None:
    with pytest.raises(AgentSDKError) as exc_info:
        raise_for_status(500, "server error")
    assert exc_info.value.status_code == 500


def test_raise_for_status_200_ok() -> None:
    raise_for_status(200, "ok")


def test_raise_for_status_201_ok() -> None:
    raise_for_status(201, "created")
