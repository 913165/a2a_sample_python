import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from client.client_agent import CloudRunAgentClient


def call_remote_a2a_agent(
    message: str,
    session_id: str = "client-session",
    method: str = "tasks/send",
) -> dict:
    """Send a message to the deployed remote A2A agent and return its raw response."""
    remote_url = os.getenv("REMOTE_AGENT_URL")
    if not remote_url:
        raise ValueError("REMOTE_AGENT_URL is required")

    bearer_token = os.getenv("REMOTE_BEARER_TOKEN")
    client = CloudRunAgentClient(agent_url=remote_url, bearer_token=bearer_token)
    return client.send_text(text=message, session_id=session_id, method=method)


LITELLM_MODEL = os.getenv("LITELLM_MODEL", "gemini/gemini-2.5-flash-lite")

root_agent = Agent(
    name="local_proxy_agent",
    model=LiteLlm(model=LITELLM_MODEL),
    description="Local client-side agent that forwards requests to a remote A2A agent.",
    instruction=(
        "You are a local proxy agent. Always use the call_remote_a2a_agent tool "
        "to send the user's request to the remote A2A agent. Return the remote "
        "agent response clearly."
    ),
    tools=[call_remote_a2a_agent],
)

