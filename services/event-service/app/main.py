from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.database import connect_to_mongo, close_mongo_connection
from app.routers import events as events_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(lifespan=lifespan)

app.include_router(events_router.router)
