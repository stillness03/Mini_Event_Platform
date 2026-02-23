from redis.asyncio import Redis
from app.core.config import get_settings

settings = get_settings()

redis_client: Redis | None = None

def create_redis() -> Redis:
    global redis_client
    if redis_client is None:
        redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
    return redis_client

async def get_redis() -> Redis:
    return create_redis()