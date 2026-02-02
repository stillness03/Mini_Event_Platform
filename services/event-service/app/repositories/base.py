from motor.motor_asyncio import AsyncIOMotorDatabase


class BaseRepository:
    collection_name: str

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[self.collection_name]