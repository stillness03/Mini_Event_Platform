import base64
import json
from datetime import datetime

from shared import UserContext
from app.repositories.event import EventRepository
from app.cache.cache_service import CacheService
from app.core.policies.event import EventPolicy
from app.schemas.events import EventCreate, EventUpdate
from app.core.config import get_settings

settings = get_settings()

class EventService:
    def __init__(self, repo: EventRepository, cache: CacheService):
        self.repo = repo
        self.cache = cache


    async def create_event(self, event: EventCreate, user: UserContext):
        result = await self.repo.create_event(event, user.user_id)

        await self.cache.delete_pattern(f"user_events:{user.user_id}:*")

        return result.model_dump(mode="json")


    async def get_event(self, event_id: str):
        cache_key = f"event:{event_id}"
    
        cached = await self.cache.get(cache_key)
        if cached is not None:
            return cached
    
        event = await self.repo.get_by_id(event_id)
        if not event:
            return None
    
        data = event.model_dump(mode="json")
        await self.cache.set(cache_key, data, ttl=settings.CACHE_EVENT_TTL)
        return data

    async def list_my_events(
            self, user: UserContext, 
            limit: int, cursor: str | None,
        ):
        cache_key = f"user_events:{user.user_id}:{limit}:{cursor or 'start'}"

        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        last_created_at = None
        last_id = None

        if cursor:
            try:
                decoded = json.loads(base64.b64decode(cursor))
                last_created_at = datetime.fromisoformat(decoded["created_at"])
                last_id = decoded["id"]
            except Exception:
                raise ValueError("Invalid cursor")

        events = await self.repo.list_by_owner(
            user_id=user.user_id,
            limit=limit,
            last_created_at=last_created_at,
            last_id=last_id,
        )

        items = [event.model_dump(mode="json") for event in events]

        next_cursor = None
        if events:
            last = events[-1]
            payload = {
                "created_at": last.created_at.isoformat(),
                "id": last.id,
            }
            next_cursor = base64.b64encode(
                json.dumps(payload).encode()
            ).decode()

        result = {
            "items": items,
            "next_cursor": next_cursor,
        }

        await self.cache.set(cache_key, result, ttl=settings.CACHE_USER_EVENTS_TTL)

        return result


    async def delete_event(self, event_id: str, user: UserContext):
        event = await self.repo.get_by_id(event_id)
        if not event:
            return False

        if not EventPolicy.can_modify(event.model_dump(), user):
            raise PermissionError("Not allowed")

        success = await self.repo.delete(event_id)
        if not success:
            return False

        
        await self.cache.delete(f"event:{event_id}")
        await self.cache.delete_pattern(
            f"user_events:{user.user_id}:*"
        )

        return True

    async def update_event(
            self, event_id: str, update: EventUpdate, 
            user: UserContext
        ):
        event = await self.repo.get_by_id(event_id)
        if not event:
            return None

        if not EventPolicy.can_modify(event.model_dump(), user):
            raise PermissionError("Not allowed")

        updated = await self.repo.update(event_id, update)
        if not updated:
            return None

        await self.cache.delete(f"event:{event_id}")
        await self.cache.delete_pattern(
            f"user_events:{user.user_id}:*"
        )

        return updated.model_dump(mode="json")