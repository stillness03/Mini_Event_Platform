from fastapi import Depends, HTTPException, status
from shared import verify_access_token
from shared import UserContext

from app.repositories.event import EventRepository
from app.cache.cache_service import CacheService
from app.core.config import get_settings
from app.cache.dep_cache import get_cache
from app.core.dependencies import get_current_user

settings = get_settings()

async def event_creation_rate_limit(
    cache: CacheService = Depends(get_cache),
    user: UserContext = Depends(get_current_user),
):
    key = f"rate_limit:event_create:{user.user_id}"
    
    count = await cache.incr_with_ttl(key, 60)

    if count > settings.MAX_EVENTS_PER_HOUR:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Event creation limit exceeded",
        )
