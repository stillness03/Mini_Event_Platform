from pymongo import ASCENDING, DESCENDING


async def create_event_indexes(db):
    await db.events.create_index(
        [("owner_id", ASCENDING), ("created_at", DESCENDING)]
    )
