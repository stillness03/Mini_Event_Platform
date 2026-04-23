from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def commit(self):
        await self.db.commit()

    async def refresh(self, instance):
        await self.db.refresh(instance)
        return instance

    async def flush(self):
        await self.db.flush()

    async def rollback(self):
        await self.db.rollback()