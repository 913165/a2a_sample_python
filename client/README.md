# Client Sample

This folder contains a local client-side agent and a small HTTP client for a deployed Cloud Run A2A agent.

## Files

- `agent.py`: local ADK proxy agent (`root_agent`) that forwards to remote A2A.
- `client_agent.py`: reusable HTTP client class + CLI utility.
- `__init__.py`: package exports.

## Required

- `REMOTE_AGENT_URL`: deployed remote A2A agent URL.
- `GOOGLE_API_KEY`: needed by the local ADK model.

## Optional

- `REMOTE_BEARER_TOKEN`: identity token for IAM-protected Cloud Run.
- `LITELLM_MODEL`: override local model (default `gemini/gemini-2.5-flash-lite`).

## Local proxy agent

`client/agent.py` defines `root_agent` and tool `call_remote_a2a_agent(...)`.
The tool sends user text to the remote A2A endpoint (`tasks/send`) and returns the raw JSON response.

## HTTP client utility usage

```bash
python client/client_agent.py --agent-url https://YOUR_SERVICE_URL
python client/client_agent.py --agent-url https://YOUR_SERVICE_URL --message "add meeting tomorrow at 10am"
```

If the service is IAM-protected, pass a token with `--bearer-token`.
