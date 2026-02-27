from redis.asyncio import Redis, ConnectionPool
from app.core.config import get_settings

settings = get_settings()
_pool: ConnectionPool | None = None

def create_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
            socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
        )
    return _pool

def get_redis() -> Redis:
    return Redis(connection_pool=create_pool())

async def close_redis():
    global _pool
    if _pool:
        await _pool.disconnect()
        _pool = None