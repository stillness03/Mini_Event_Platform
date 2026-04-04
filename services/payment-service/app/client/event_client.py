import random

import httpx
from fastapi import Depends
import asyncio
import logging

from app.clients.deps import get_http_client
from app.core.config import get_settings


logger = logging.getLogger(__name__)

class EventNotFound(Exception):
    pass

class EventServiceUnavailable(Exception):
    """Event service is unavailable after retries"""
    pass


class EventClient:

    def __init__(self, http_client: httpx.AsyncClient = Depends(get_http_client)):
        self.client = http_client
        self.settings = get_settings()
        self.base_url = self.settings.EVENTS_BASE_URL

    async def get_event(self, event_id: str):

        max_retries = 3
        base_delay = 0.5 # seconds

        for attempt in range(max_retries):
            try:
                response = await self.client.get(
                    f"{self.base_url}/events/{event_id}",
                    timeout=5.0,
                )
                if response.status_code == 200:
                    return response.json()

                if response.status_code == 404:
                    raise EventNotFound(f"Event {event_id} not found")

                response.raise_for_status()


            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                logger.warning(
                    "Attempt %s failed for event %s: %s",
                    attempt + 1, event_id, str(e)
                )

                if attempt == max_retries - 1:
                    raise EventServiceUnavailable(
                        "Event service is dead after retries"
                    ) from e

                delay = base_delay * (2 ** attempt) + random.uniform(0, 0.1)
                await asyncio.sleep(delay)

        raise EventServiceUnavailable()


def get_event_client(
    http_client: httpx.AsyncClient = Depends(get_http_client),
) -> EventClient:
    return EventClient(http_client)