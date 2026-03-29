import logging
from fastapi import Header, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.event import EventRepository
from app.cache.cache_service import CacheService
from app.cache.dep_cache import get_cache
from app.service.event_service import EventService
from shared.auth import verify_access_token
from shared.schemas import UserContext
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

async def get_current_user(
    x_user_id: str = Header(None, alias="X-User-Id"),
    x_user_role: str = Header("user", alias="X-User-Role")
) -> UserContext:
    if not x_user_id:
        logger.error("422 Error: X-User-Id header is missing in request from Gateway")
        raise HTTPException(status_code=401, detail="Identity missing")

    return UserContext(user_id=x_user_id, role=x_user_role)