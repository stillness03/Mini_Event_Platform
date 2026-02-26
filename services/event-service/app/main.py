from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.database import connect_to_mongo, close_mongo_connection
from app.routers import events as events_router
from app.cache.redis_client import close_redis, create_pool, get_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    create_pool()
    
    redis = get_redis()
    await redis.ping()
    
    yield
    
    await close_redis()
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

app.include_router(events_router.router)
