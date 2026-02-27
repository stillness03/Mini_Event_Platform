from fastapi import Depends
from redis.asyncio import Redis
from app.cache.cache_service import CacheService
from app.cache.redis_client import get_redis

def get_cache(redis: Redis = Depends(get_redis)) -> CacheService:
    return CacheService(redis)