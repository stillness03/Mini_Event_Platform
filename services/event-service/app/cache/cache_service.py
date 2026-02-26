import logging
import json
from typing import Any
from redis.asyncio import Redis
from redis.exceptions import RedisError
from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

class CacheService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> Any | None:
        try:
            value = await self.redis.get(key)
            if value is None:
                return None
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except RedisError as e:
            logger.warning("Cache GET failed for key=%s: %s", key, e)
            return None
    
    async def set(
            self, key: str, value: Any, 
            ttl: int = settings.CACHE_DEFAULT_TTL):
        try:
            if hasattr(value, "model_dump_json"):
                payload = value.model_dump_json()
            else:
                payload = json.dumps(value, default=str)

            await self.redis.set(
                key,
                payload,
                ex=ttl,
            )
        except RedisError as e:
            logger.warning("Cache SET failed for key=%s: %s", key, e)

    async def set_int(self, key: str, value: int, ttl: int = settings.CACHE_DEFAULT_TTL):
        try:
            await self.redis.set(key, value, ex=ttl)
        except RedisError as e:
            logger.warning("Cache SET_INT failed for key=%s: %s", key, e)

    async def incr(self, key: str) -> int:
        try:
            return await self.redis.incr(key)
        except RedisError as e:
            logger.warning("Cache INCR failed for key=%s: %s", key, e)
            return 0

    async def delete(self, key: str):
        try:
            await self.redis.delete(key)
        except RedisError as e:
            logger.warning("Cache DELETE failed for key=%s: %s", key, e)

    async def delete_pattern(self, pattern: str):
        try:
            keys = [key async for key in self.redis.scan_iter(pattern)]
            if keys:
                await self.redis.delete(*keys)
        except RedisError as e:
            logger.warning("Cache DELETE_PATTERN failed for pattern=%s: %s", pattern, e)


    async def incr_with_ttl(self, key: str, ttl: int) -> int:
        try:
            count = await self.redis.incr(key)
            if count == 1:
                await self.redis.expire(key, ttl)
            return count
        except RedisError as e:
            logger.warning("Cache INCR_WITH_TTL failed for key=%s: %s", key, e)
            return 0