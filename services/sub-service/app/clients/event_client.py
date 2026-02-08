import httpx
from fastapi import Depends
import asyncio
import logging

from app.clients.deps import get_http_client
from app.core.config import get_settings


logger = logging.getLogger(__name__)

class EventServiceUnavailable(Exception):
    """Event service is unavailable after retries"""
    pass


class EventClient:

    def __init__(self, http_client: httpx.AsyncClient):
        self.client = http_client
        self.settings = get_settings()
        self.base_url = self.settings.EVENT_SERVICE_URL

    async def get_event(self, event_id: int):
        
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
                    return None

                logger.warning(
                    "Unexpected status from event service: %s",
                    response.status_code,
                )

            except httpx.RequestError as e:
                logger.warning(
                    "Event service request failed (attempt %s): %s",
                    attempt + 1,
                    str(e),
                )

                if attempt == max_retries - 1:
                    raise EventServiceUnavailable() from e

                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)

        raise EventServiceUnavailable()



def get_event_client(
    http_client: httpx.AsyncClient = Depends(get_http_client),
) -> EventClient:
    return EventClient(http_client)