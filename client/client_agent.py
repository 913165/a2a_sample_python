import argparse
import json
import os
import uuid
from dataclasses import dataclass
from typing import Any
from urllib import request
from urllib.error import HTTPError, URLError


@dataclass
class CloudRunAgentClient:
    """Small client for talking to a deployed A2A agent on Cloud Run."""

    agent_url: str
    bearer_token: str | None = None
    timeout_seconds: int = 30

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        return headers

    def _request_json(
        self, url: str, method: str = "GET", payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")

        req = request.Request(url=url, data=data, headers=self._headers(), method=method)
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else {}
        except HTTPError as exc:
            raise RuntimeError(
                f"HTTP {exc.code} from {url}: {exc.read().decode('utf-8', errors='ignore')}"
            ) from exc
        except URLError as exc:
            raise RuntimeError(f"Network error calling {url}: {exc}") from exc

    def get_agent_card(self) -> dict[str, Any]:
        base = self.agent_url.rstrip("/")
        return self._request_json(f"{base}/.well-known/agent-card.json")

    def send_text(
        self,
        text: str,
        session_id: str = "client-session",
        method: str = "tasks/send",
    ) -> dict[str, Any]:
        """Send a plain-text message using JSON-RPC over the root endpoint."""
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method,
            "params": {
                "sessionId": session_id,
                "message": {
                    "role": "user",
                    "parts": [
                        {
                            "type": "text",
                            "text": text,
                        }
                    ],
                },
            },
        }
        return self._request_json(self.agent_url.rstrip("/"), method="POST", payload=payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Client for deployed Cloud Run A2A agent")
    parser.add_argument(
        "--agent-url",
        default=os.getenv("AGENT_URL", ""),
        help="Base URL of deployed agent, e.g. https://sample-a2a-agent-xyz.a.run.app",
    )
    parser.add_argument(
        "--bearer-token",
        default=os.getenv("BEARER_TOKEN", None),
        help="Optional bearer token for IAM-protected service",
    )
    parser.add_argument("--message", help="Message to send", default=None)
    args = parser.parse_args()

    if not args.agent_url:
        raise SystemExit("Set --agent-url or AGENT_URL")

    client = CloudRunAgentClient(args.agent_url, args.bearer_token)

    card = client.get_agent_card()
    print("Agent card:")
    print(json.dumps(card, indent=2))

    if args.message:
        print("\nResponse:")
        response = client.send_text(args.message)
        print(json.dumps(response, indent=2))


if __name__ == "__main__":
    main()

