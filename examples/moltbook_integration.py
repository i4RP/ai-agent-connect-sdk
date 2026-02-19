"""Moltbook provider integration example."""

from ai_agent_sdk import AgentConnectClient

client = AgentConnectClient(
    api_key="moltbook_xxx",
    app_key="moltdev_xxx",
    provider="moltbook",
)

profile = client.get_agent_profile()
print(f"Agent: {profile.name}")
print(f"Karma: {profile.karma}")
print(f"Verified: {profile.is_verified}")

token = client.generate_identity_token()
print(f"Identity token generated (expires: {token.expires_at})")

result = client.verify_identity(token.token)
if result.valid and result.agent:
    print(f"Verified agent: {result.agent.name}")
else:
    print(f"Verification failed: {result.error}")

client.close()
