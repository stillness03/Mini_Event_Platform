from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ReadPreference
from app.core.config import get_settings
from app.indexes.events import create_event_indexes

settings = get_settings()

if settings.MONGO_URI is None or settings.DB_NAME is None:
    raise ValueError("MONGO_URI and DB_NAME must be set in environment variables")


class MongoDb:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None

mongo_db = MongoDb()


async def connect_to_mongo() -> None:
    mongo_db.client = AsyncIOMotorClient(
        settings.MONGO_URI,
        maxPoolSize=100,
        minPoolSize=20,
        serverSelectionTimeoutMS=5000,
        read_preference=ReadPreference.SECONDARY_PREFERRED,
        uuidRepresentation="standard",
    )
    mongo_db.db = mongo_db.client[settings.DB_NAME]

    await create_event_indexes(mongo_db.db)


async def close_mongo_connection() -> None:
    if mongo_db.client:
        mongo_db.client.close()


def get_db() -> AsyncIOMotorDatabase:
    if mongo_db.db is None:
        raise RuntimeError("MongoDB is not initialized")
    return mongo_db.db
