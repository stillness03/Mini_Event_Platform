from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Header, HTTPException, status
from fastapi import Depends
from uuid import UUID
from shared import UserContext

from app.repositories.event import EventRepository
from app.core.database import get_db
from app.cache.cache_service import CacheService
from app.core.config import get_settings
from app.cache.dep_cache import get_cache


settings = get_settings()

def get_event_repo(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> EventRepository:
    return EventRepository(db)


def get_current_user(
    x_user_id: UUID | None = Header(None),
    x_user_role: str | None = Header("user"),
) -> UserContext:
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthenticated",
        )

    return UserContext(
        owner_id=x_user_id, # for tests
        role=x_user_role,
    )

async def event_creation_rate_limit(
    cache: CacheService = Depends(get_cache),
    user: UserContext = Depends(get_current_user),
):
    key = f"rate_limit:event_create:{user.owner_id}"
    
    count = await cache.incr_with_ttl(key, 60)

    if count > settings.MAX_EVENTS_PER_HOUR:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Event creation limit exceeded",
        )
