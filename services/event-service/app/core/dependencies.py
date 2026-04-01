import logging
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.event import EventRepository
from app.cache.cache_service import CacheService
from app.cache.dep_cache import get_cache
from app.service.event_service import EventService
from app.core.config import get_settings
from app.core.database import get_db

logger = logging.getLogger("event-service.auth")
settings = get_settings()

def get_event_repo(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> EventRepository:
    return EventRepository(db)

def get_event_service(
    repo: EventRepository = Depends(get_event_repo),
    cache: CacheService = Depends(get_cache),
):
    return EventService(repo, cache)

