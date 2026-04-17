# ADK Agent

This sample uses the Agent Development Kit (ADK) to create a simple calendar update Agent which communicates using A2A.

## Prerequisites

- Python 3.13 or higher
- Access to an LLM and API Key

## Running the Sample

1. Navigate to the samples directory:

```shell
cd samples/python/agents/adk_cloud_run
```

2. Create and activate a virtual environment:

```shell
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```shell
python -m pip install --upgrade pip
python -m pip install -e .
```

4. Create an environment file:

```shell
echo "GOOGLE_API_KEY=your_api_key_here" > .env
# Optional for local runs (defaults to http://localhost:10002):
echo "APP_URL=http://localhost:10002" >> .env
```

5. Run the agent:

```shell
python __main__.py --host localhost --port 10002
```

## Setup Config Google Cloud Run

### Create Service Account

Cloud Run uses [service accounts (SA)](https://cloud.google.com/run/docs/configuring/service-accounts) when running service instances. Create a service account specific for the deployed A2A service.

```shell
gcloud iam service-accounts create a2a-service-account \
  --description="service account for a2a cloud run service" \
  --display-name="A2A cloud run service account"
```

### Add IAM access

Below roles allow cloud run service to access secrets and invoke `predict` API on Vertex AI models.

```shell
gcloud projects add-iam-policy-binding "{your-project-id}" \
  --member="serviceAccount:a2a-service-account@{your-project-id}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --role="roles/aiplatform.user"
```

## Deploy to Google Cloud Run

The A2A cloud run service can be [exposed publicly](https://cloud.google.com/run/docs/authenticating/public) or kept internal to just GCP clients.

When deploying a service to Cloud Run, it returns a `run.app` URL to query the running service.

### Service Authentication

#### IAM based Authentication

IAM can be used for [service-to-service authentication](https://cloud.google.com/run/docs/authenticating/service-to-service) if the clients are within GCP. Agentspace is one such example of an internal client. The clients can use service accounts and they need to be given IAM role: `roles/run.invoker`

#### Public Access

The A2A server is responsible for handling agent level auth. They need to provide this auth info in their agent card using the securitySchemes and security params.

Use the param `--allow-unauthenticated` while deploying to cloud run, to allow public access.

### Deploy

```shell
gcloud run deploy sample-a2a-agent \
    --port=8080 \
    --source=. \
    --no-allow-unauthenticated \
    --memory "1Gi" \
    --region="us-central1" \
    --project="{your-project-id}" \
    --service-account a2a-service-account \
    --set-env-vars=GOOGLE_GENAI_USE_VERTEXAI=true,\
GOOGLE_CLOUD_PROJECT="{your-project-id}",\
GOOGLE_CLOUD_LOCATION="us-central1",\
APP_URL="TEMPORARY_URL"
```

### Update Service with the Service URL

After the deploy command completes, it will output the service URL. Update the running service to set the `APP_URL` environment variable with this new URL.

```shell
gcloud run services update sample-a2a-agent \
  --project="{your-project-id}" \
  --region="us-central1" \
  --update-env-vars=APP_URL="{your-cloud-run-service-url}"
```

## Testing your Agent

You can test your live agent with the A2A CLI, available at `a2a-samples/samples/python/hosts/cli`.

The following command allows you to authenticate and interact with your A2A enabled agent in Cloud Run.

```shell
cd /path/to/cli
uv run . --agent {your-cloud-run-service-url} --bearer-token "$(gcloud auth print-identity-token)"
```

## Disclaimer

Important: The sample code provided is for demonstration purposes and illustrates the mechanics of the Agent-to-Agent (A2A) protocol. When building production applications, it is critical to treat any agent operating outside of your direct control as a potentially untrusted entity.

All data received from an external agent—including but not limited to its AgentCard, messages, artifacts, and task statuses—should be handled as untrusted input.

For example, a malicious agent could provide an AgentCard containing crafted data in its fields (e.g., description, name, skills.description). If this data is used without sanitization to construct prompts for a Large Language Model (LLM), it could expose your application to prompt injection attacks. Failure to properly validate and sanitize this data before use can introduce security vulnerabilities into your application.

Developers are responsible for implementing appropriate security measures, such as input validation and secure handling of credentials to protect their systems and users.
"# a2a_sample_python" 
