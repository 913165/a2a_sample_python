FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

EXPOSE 8080
WORKDIR /app

COPY . ./

RUN uv sync

ENTRYPOINT ["uv", "run", ".", "--host", "0.0.0.0", "--port", "8080"]

# To build the Docker image, run:
# docker build -t tinumistry/my-fastapi-app:1.0 .
# to push to a registry, tag the image and push:
# docker push tinumistry/my-fastapi-app:1.0
# gcp shell
# docker pull tinumistry/my-fastapi-app:1.0
# docker tag tinumistry/my-fastapi-app:1.0 us-central1-docker.pkg.dev/agentverse-summoner-xl71u6zdlk/docker002/my-fastapi-app:latest
# docker push us-central1-docker.pkg.dev/agentverse-summoner-xl71u6zdlk/docker002/my-fastapi-app:latest