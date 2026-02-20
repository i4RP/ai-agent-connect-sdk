"""Async client usage example."""

import asyncio

from ai_agent_sdk import AsyncAgentConnectClient


async def main() -> None:
    async with AsyncAgentConnectClient(
        api_key="your-api-key",
        provider="moltbook",
    ) as client:
        profile = await client.get_agent_profile()
        print(f"Agent: {profile.name}")

        token = await client.generate_identity_token(scopes=["read"])
        print(f"Token: {token.token[:20]}...")

        apps = await client.list_apps(page=1, per_page=5)
        for app in apps.items:
            print(f"  - {app}")


if __name__ == "__main__":
    asyncio.run(main())
