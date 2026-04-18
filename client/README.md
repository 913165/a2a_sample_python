# Client Sample

This folder contains a minimal client for a deployed Cloud Run agent.

## Files

- `client_agent.py`: reusable client class + CLI entrypoint.
- `__init__.py`: export helper.

## Required

- `AGENT_URL`: your deployed agent URL.

## Optional

- `BEARER_TOKEN`: identity token if your Cloud Run service is not public.

## Example usage

```bash
python client/client_agent.py --agent-url https://YOUR_SERVICE_URL
python client/client_agent.py --agent-url https://YOUR_SERVICE_URL --message "add meeting tomorrow at 10am"
```

If the service is IAM-protected, pass a token with `--bearer-token`.

