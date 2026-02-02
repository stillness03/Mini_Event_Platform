import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv


load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")


if MONGO_URI is None or DB_NAME is None:
    raise ValueError("MONGO_URI and DB_NAME must be set in environment variables")


class MongoDb:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None

mongo_db = MongoDb()


async def connect_to_mongo() -> None:
    mongo_db.client = AsyncIOMotorClient(
        MONGO_URI,
        maxPoolSize=50,
        minPoolSize=10,
        serverSelectionTimeoutMS=5000,
    )
    mongo_db.db = mongo_db.client[DB_NAME]


async def close_mongo_connection() -> None:
    if mongo_db.client:
        mongo_db.client.close()


def get_db() -> AsyncIOMotorDatabase:
    if mongo_db.db is None:
        raise RuntimeError("MongoDB is not initialized")
    return mongo_db.db