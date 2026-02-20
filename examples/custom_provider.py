"""Custom provider example for integrating with your own platform."""

from ai_agent_sdk import AgentConnectClient, AuthStrategy, CustomProvider

provider = CustomProvider(
    provider_name="my-platform",
    provider_base_url="https://api.my-platform.com/v2",
    auth_strategy=AuthStrategy.HEADER,
    auth_header="X-API-Key",
    app_auth_header="X-App-Secret",
    identity_token_path="/auth/identity-token",
    verify_identity_path="/auth/verify",
    agent_profile_path="/me",
    app_register_path="/developer/apps",
    app_list_path="/developer/apps",
)

client = AgentConnectClient(
    api_key="my-api-key",
    app_key="my-app-secret",
    provider=provider,
)

profile = client.get_agent_profile()
print(f"Agent: {profile.name}")

data = client.request("GET", "/custom/endpoint", params={"q": "test"})
print(f"Custom response: {data}")

client.close()
