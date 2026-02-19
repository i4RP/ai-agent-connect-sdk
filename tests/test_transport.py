import httpx
import pytest
import respx

from ai_agent_sdk.config import SDKConfig
from ai_agent_sdk.exceptions import AuthenticationError, NotFoundError
from ai_agent_sdk.transport import AsyncTransport, Transport


@pytest.fixture
def config() -> SDKConfig:
    return SDKConfig(
        api_key="test-key",
        base_url="https://api.example.com",
        timeout=5.0,
    )


@respx.mock
def test_transport_get(config: SDKConfig) -> None:
    respx.get("https://api.example.com/test").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    transport = Transport(config)
    response = transport.get("/test")
    assert response.status_code == 200
    assert response.json()["ok"] is True
    transport.close()


@respx.mock
def test_transport_post(config: SDKConfig) -> None:
    respx.post("https://api.example.com/data").mock(
        return_value=httpx.Response(201, json={"id": "1"})
    )
    transport = Transport(config)
    response = transport.post("/data", json={"name": "test"})
    assert response.status_code == 201
    transport.close()


@respx.mock
def test_transport_raises_on_401(config: SDKConfig) -> None:
    respx.get("https://api.example.com/secure").mock(
        return_value=httpx.Response(401, text="unauthorized")
    )
    transport = Transport(config)
    with pytest.raises(AuthenticationError):
        transport.get("/secure")
    transport.close()


@respx.mock
def test_transport_raises_on_404(config: SDKConfig) -> None:
    respx.get("https://api.example.com/missing").mock(
        return_value=httpx.Response(404, text="not found")
    )
    transport = Transport(config)
    with pytest.raises(NotFoundError):
        transport.get("/missing")
    transport.close()


@respx.mock
def test_transport_parses_rate_limit_headers(config: SDKConfig) -> None:
    respx.get("https://api.example.com/limited").mock(
        return_value=httpx.Response(
            200,
            json={"ok": True},
            headers={"X-RateLimit-Limit": "100", "X-RateLimit-Remaining": "42"},
        )
    )
    transport = Transport(config)
    transport.get("/limited")
    info = transport.last_rate_limit
    assert info is not None
    assert info.limit == 100
    assert info.remaining == 42
    transport.close()


@respx.mock
def test_transport_put(config: SDKConfig) -> None:
    respx.put("https://api.example.com/item/1").mock(
        return_value=httpx.Response(200, json={"updated": True})
    )
    transport = Transport(config)
    response = transport.put("/item/1", json={"name": "updated"})
    assert response.json()["updated"] is True
    transport.close()


@respx.mock
def test_transport_delete(config: SDKConfig) -> None:
    respx.delete("https://api.example.com/item/1").mock(
        return_value=httpx.Response(204)
    )
    transport = Transport(config)
    response = transport.delete("/item/1")
    assert response.status_code == 204
    transport.close()


@respx.mock
def test_transport_sets_auth_header(config: SDKConfig) -> None:
    route = respx.get("https://api.example.com/check").mock(
        return_value=httpx.Response(200, json={})
    )
    transport = Transport(config)
    transport.get("/check")
    request = route.calls[0].request
    assert "Bearer test-key" in request.headers.get("Authorization", "")
    transport.close()


def test_transport_close_idempotent(config: SDKConfig) -> None:
    transport = Transport(config)
    transport.close()
    transport.close()


@pytest.mark.asyncio
@respx.mock
async def test_async_transport_get(config: SDKConfig) -> None:
    respx.get("https://api.example.com/test").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    transport = AsyncTransport(config)
    response = await transport.get("/test")
    assert response.status_code == 200
    await transport.close()


@pytest.mark.asyncio
@respx.mock
async def test_async_transport_post(config: SDKConfig) -> None:
    respx.post("https://api.example.com/data").mock(
        return_value=httpx.Response(201, json={"id": "1"})
    )
    transport = AsyncTransport(config)
    response = await transport.post("/data", json={"value": 1})
    assert response.status_code == 201
    await transport.close()
