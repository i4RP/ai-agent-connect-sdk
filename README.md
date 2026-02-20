# AI Agent Connect SDK

A general-purpose Python SDK for API connections to distribute and connect apps with AI agents. Inspired by platforms like [Moltbook](https://www.moltbook.com), this SDK provides a versatile, provider-agnostic interface for agent authentication, identity verification, and app distribution.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Multi-Provider Support** - Built-in Moltbook provider + fully customizable provider system
- **Agent Authentication** - Token-based identity verification for AI agents
- **App Registry** - Register, discover, and manage apps for AI agent consumption
- **Transport Layer** - httpx-based HTTP client with automatic error handling
- **Middleware Pipeline** - Extensible retry, rate limiting, and logging middleware
- **Async Support** - Full async/await support with `AsyncAgentConnectClient`
- **Type Safety** - Pydantic models with full type annotations

## Installation

```bash
pip install ai-agent-connect
```

For development:

```bash
pip install ai-agent-connect[dev]
```

## Quick Start

### With Moltbook

```python
from ai_agent_sdk import AgentConnectClient

client = AgentConnectClient(
    api_key="moltbook_xxx",
    provider="moltbook",
)

profile = client.get_agent_profile()
print(f"Agent: {profile.name} (karma: {profile.karma})")

token = client.generate_identity_token(scopes=["read", "write"])
print(f"Token: {token.token[:20]}...")

client.close()
```

### With a Custom Platform

```python
from ai_agent_sdk import AgentConnectClient, CustomProvider, AuthStrategy

provider = CustomProvider(
    provider_name="my-platform",
    provider_base_url="https://api.my-platform.com/v2",
    auth_strategy=AuthStrategy.HEADER,
    auth_header="X-API-Key",
    identity_token_path="/auth/token",
    verify_identity_path="/auth/verify",
)

client = AgentConnectClient(
    api_key="my-api-key",
    provider=provider,
)

profile = client.get_agent_profile()
print(f"Agent: {profile.name}")
client.close()
```

### With Base URL Only

```python
from ai_agent_sdk import AgentConnectClient

client = AgentConnectClient(
    api_key="my-key",
    base_url="https://api.example.com/v1",
)

data = client.request("GET", "/agents/me")
print(data)
client.close()
```

## Identity Verification

Verify AI agent identities when they authenticate with your app:

```python
from ai_agent_sdk import AgentConnectClient

client = AgentConnectClient(
    api_key="agent-key",
    app_key="your-app-key",
    provider="moltbook",
)

# Agent generates an identity token
token = client.generate_identity_token()

# App verifies the token
result = client.verify_identity(token.token)
if result.valid and result.agent:
    print(f"Verified: {result.agent.name} (karma: {result.agent.karma})")
```

## App Registration

Register your app so AI agents can discover and use it:

```python
from ai_agent_sdk import AgentConnectClient, AppCapability

client = AgentConnectClient(
    api_key="your-key",
    provider="moltbook",
)

app = client.register_app(
    name="MyApp",
    description="A demo app for AI agents",
    base_url="https://myapp.example.com/api",
    capabilities=[
        AppCapability(
            name="search",
            description="Search for items",
            endpoint="/search",
            method="GET",
            parameters={"q": "string"},
        ),
    ],
)
print(f"Registered: {app.app_id}")
```

## Integration Examples

This SDK can connect AI agents to **any service with a REST API**. Below are concrete examples for common use cases.

### Soccer Game Integration

Connect AI agents to a multiplayer soccer game server:

```python
from ai_agent_sdk import AgentConnectClient, CustomProvider, AppCapability

provider = CustomProvider(
    provider_name="soccer-game",
    provider_base_url="https://api.soccer-game.com/v1",
    agent_profile_path="/players/me",
)

client = AgentConnectClient(api_key="game-api-key", provider=provider)

# Register the game's capabilities for AI agents
client.register_app(
    name="SoccerGameBot",
    description="AI agents can join and play soccer matches via API",
    base_url="https://api.soccer-game.com/v1",
    capabilities=[
        AppCapability(
            name="join_match",
            description="Join an active soccer match",
            endpoint="/matches/join",
            method="POST",
        ),
        AppCapability(
            name="kick_ball",
            description="Kick the ball with direction and power",
            endpoint="/actions/kick",
            method="POST",
            parameters={"direction": "float", "power": "float"},
        ),
        AppCapability(
            name="move_player",
            description="Move the player to a position",
            endpoint="/actions/move",
            method="POST",
            parameters={"x": "float", "y": "float"},
        ),
        AppCapability(
            name="get_score",
            description="Get the current match score",
            endpoint="/matches/score",
            method="GET",
        ),
    ],
)

# AI agent performs in-game actions
client.request("POST", "/matches/join", json={"match_id": "match-123"})
client.request("POST", "/actions/kick", json={"direction": 45.0, "power": 0.8})
score = client.request("GET", "/matches/score")
print(f"Score: {score}")

client.close()
```

### DEX (Decentralized Exchange) Integration

Connect AI agents to a DEX for automated token trading:

```python
from ai_agent_sdk import AgentConnectClient, CustomProvider, AppCapability, AuthStrategy

provider = CustomProvider(
    provider_name="dex-platform",
    provider_base_url="https://api.my-dex.com/v1",
    auth_strategy=AuthStrategy.HEADER,
    auth_header="X-API-Key",
)

client = AgentConnectClient(api_key="dex-api-key", provider=provider)

# Register DEX capabilities for AI agents
client.register_app(
    name="DEX Trading Bot",
    description="AI agents can trade tokens on the DEX",
    base_url="https://api.my-dex.com/v1",
    capabilities=[
        AppCapability(
            name="get_price",
            description="Get token pair price",
            endpoint="/tokens/price",
            method="GET",
            parameters={"pair": "string"},
        ),
        AppCapability(
            name="swap",
            description="Swap tokens",
            endpoint="/swap",
            method="POST",
            parameters={
                "from_token": "string",
                "to_token": "string",
                "amount": "float",
            },
            required_scopes=["trade"],
        ),
        AppCapability(
            name="get_liquidity",
            description="Get liquidity pool info",
            endpoint="/pools",
            method="GET",
        ),
        AppCapability(
            name="get_balance",
            description="Get wallet balance",
            endpoint="/wallet/balance",
            method="GET",
        ),
    ],
)

# AI agent operates on the DEX
price = client.request("GET", "/tokens/price", params={"pair": "ETH/USDC"})
print(f"ETH/USDC price: {price}")

balance = client.request("GET", "/wallet/balance")
print(f"Wallet balance: {balance}")

swap_result = client.request("POST", "/swap", json={
    "from_token": "ETH",
    "to_token": "USDC",
    "amount": 1.5,
})
print(f"Swap result: {swap_result}")

client.close()
```

### Other Use Cases

The SDK works with **any REST API**. Some additional examples:

| Use Case | Description |
|----------|-------------|
| **SNS / Social** | AI agents posting, commenting, and interacting on social platforms |
| **E-commerce** | AI agents browsing products, placing orders, managing inventory |
| **IoT / Robotics** | AI agents controlling sensors, devices, and robots via API |
| **Data Analytics** | AI agents querying dashboards, generating reports |
| **Customer Support** | AI agents handling tickets, responding to inquiries |
| **NFT Marketplace** | AI agents minting, listing, and trading NFTs |

## Async Support

```python
import asyncio
from ai_agent_sdk import AsyncAgentConnectClient

async def main():
    async with AsyncAgentConnectClient(
        api_key="your-key",
        provider="moltbook",
    ) as client:
        profile = await client.get_agent_profile()
        print(f"Agent: {profile.name}")

asyncio.run(main())
```

## Configuration

### Via Constructor

```python
client = AgentConnectClient(
    api_key="your-key",
    app_key="your-app-key",
    base_url="https://api.example.com",
    timeout=30.0,
    retries=3,
    retry_delay=1.0,
    custom_headers={"X-Custom": "value"},
)
```

### Via Environment Variables

```bash
export AGENT_SDK_API_KEY=your-key
export AGENT_SDK_APP_KEY=your-app-key
export AGENT_SDK_BASE_URL=https://api.example.com
export AGENT_SDK_PROVIDER=moltbook
export AGENT_SDK_TIMEOUT=30.0
```

```python
client = AgentConnectClient.from_env()
```

Custom prefix:

```python
client = AgentConnectClient.from_env(prefix="MYAPP")
# Reads MYAPP_API_KEY, MYAPP_BASE_URL, etc.
```

## Middleware

### Retry Middleware

```python
from ai_agent_sdk.middleware import RetryMiddleware

retry = RetryMiddleware(
    max_retries=3,
    base_delay=1.0,
    max_delay=60.0,
    backoff_factor=2.0,
)
```

### Rate Limit Middleware

```python
from ai_agent_sdk.middleware import RateLimitMiddleware

rate_limiter = RateLimitMiddleware(
    max_requests=100,
    window_seconds=60.0,
)

print(f"Remaining: {rate_limiter.remaining_requests}")
print(f"Limited: {rate_limiter.is_rate_limited}")
```

### Custom Middleware

```python
from ai_agent_sdk.middleware import Middleware, MiddlewarePipeline
from ai_agent_sdk.middleware.base import RequestContext, ResponseContext

class MyMiddleware(Middleware):
    def process_request(self, context: RequestContext) -> RequestContext:
        context.headers["X-Custom"] = "value"
        return context

    def process_response(self, context: RequestContext, response: ResponseContext) -> ResponseContext:
        return response

pipeline = MiddlewarePipeline()
pipeline.add(MyMiddleware())
```

## Error Handling

```python
from ai_agent_sdk import (
    AgentSDKError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
)

try:
    profile = client.get_agent_profile()
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}s")
except NotFoundError:
    print("Resource not found")
except AgentSDKError as e:
    print(f"Error ({e.status_code}): {e.message}")
```

## Providers

| Provider | Class | Description |
|----------|-------|-------------|
| Moltbook | `MoltbookProvider` | Built-in support for Moltbook API |
| Custom | `CustomProvider` | Fully configurable for any platform |

### Creating a Custom Provider

Extend `BaseProvider` for deep integration:

```python
from ai_agent_sdk.providers.base import BaseProvider

class MyProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "my-provider"

    @property
    def base_url(self) -> str:
        return "https://api.my-provider.com"

    def build_auth_headers(self, api_key: str) -> dict[str, str]:
        return {"Authorization": f"Token {api_key}"}

    def build_app_auth_headers(self, app_key: str) -> dict[str, str]:
        return {"X-App-Key": app_key}

    # ... implement remaining abstract methods
```

## Development

```bash
git clone https://github.com/i4RP/ai-agent-connect-sdk.git
cd ai-agent-connect-sdk
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## License

MIT
