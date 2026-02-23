import json
from redis.asyncio import Redis
from app.core.config import get_settings

settings = get_settings()

class CacheService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str):
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value):
        await self.redis.set(
            key,
            json.dumps(value),
        )

    async def set_int(self, key: str, value: int):
        await self.redis.set(key, value)

    async def incr(self, key: str) -> int:
        return await self.redis.incr(key)

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def delete_pattern(self, pattern: str):
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)