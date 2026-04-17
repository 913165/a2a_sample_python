import asyncio
import functools
import logging
import os

import click
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agent import root_agent as calendar_agent
from agent_executor import ADKAgentExecutor
from dotenv import load_dotenv
from starlette.applications import Starlette


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """Exception for missing API key."""


def make_sync(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


@click.command()
@click.option('--host', default='localhost')
@click.option('--port', default=10002)
@make_sync
async def main(host, port):
    # APP_URL is required in Cloud Run, but local runs can safely derive it.
    advertised_host = 'localhost' if host in ('0.0.0.0', '::') else host
    app_url = os.getenv('APP_URL') or f'http://{advertised_host}:{port}'

    agent_card = AgentCard(
        name=calendar_agent.name,
        description=calendar_agent.description,
        version='1.0.0',
        url=app_url,
        default_input_modes=['text', 'text/plain'],
        default_output_modes=['text', 'text/plain'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[
            AgentSkill(
                id='add_calendar_event',
                name='Add Calendar Event',
                description='Creates a new calendar event.',
                tags=['calendar', 'event', 'create'],
                examples=[
                    'Add a calendar event for my meeting tomorrow at 10 AM.',
                ],
            )
        ],
    )

    # Keep the sample simple: always use in-memory task storage.
    task_store = InMemoryTaskStore()

    request_handler = DefaultRequestHandler(
        agent_executor=ADKAgentExecutor(
            agent=calendar_agent,
        ),
        task_store=task_store,
    )

    a2a_app = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )
    routes = a2a_app.routes()
    app = Starlette(
        routes=routes,
        middleware=[],
    )

    config = uvicorn.Config(app, host=host, port=port, log_level='info')
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == '__main__':
    main()
