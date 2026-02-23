from fastapi import Depends
from app.repositories.event import EventRepository
from app.cache.cache_service import CacheService
from app.cache.dep_cache import get_cache
from app.core.security import get_event_repo
from app.service.event_service import EventService


def get_event_service(
    repo: EventRepository = Depends(get_event_repo),
    cache: CacheService = Depends(get_cache),
):
    return EventService(repo, cache)