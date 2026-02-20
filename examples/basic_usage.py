"""Basic usage example for AI Agent Connect SDK."""

from ai_agent_sdk import AgentConnectClient, AppCapability

client = AgentConnectClient(
    api_key="your-api-key",
    base_url="https://api.your-platform.com/v1",
)

profile = client.get_agent_profile()
print(f"Agent: {profile.name} (karma: {profile.karma})")

token = client.generate_identity_token(scopes=["read", "write"])
print(f"Identity token: {token.token[:20]}...")

app = client.register_app(
    name="MyApp",
    description="A demo application for AI agents",
    base_url="https://myapp.example.com/api",
    capabilities=[
        AppCapability(
            name="search",
            description="Search for items",
            endpoint="/search",
            method="GET",
            parameters={"q": "string", "limit": "int"},
        ),
        AppCapability(
            name="create_item",
            description="Create a new item",
            endpoint="/items",
            method="POST",
            parameters={"title": "string", "content": "string"},
            required_scopes=["write"],
        ),
    ],
)
print(f"App registered: {app.app_id}")

apps = client.list_apps(page=1, per_page=10)
for item in apps.items:
    print(f"  - {item}")

client.close()
