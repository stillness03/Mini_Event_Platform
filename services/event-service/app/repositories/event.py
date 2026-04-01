from uuid import UUID
from datetime import datetime, timezone
from pymongo import DESCENDING

from app.repositories.base import BaseRepository
from app.schemas.events import EventCreate, EventResponse, EventUpdate
from app.models.mongo import to_object_id


class EventRepository(BaseRepository):
    collection_name = "events"

    async def create_event(
            self, event_data: EventCreate,
            user_id: UUID) -> EventResponse:
        event_data = {
            "title": event_data.title,
            "description": event_data.description,
            "owner_id": user_id,
            "created_at": datetime.now(timezone.utc),
            "schema_version": 3, # for future migrations
        }

        result = await self.collection.insert_one(event_data)
        event_data["_id"] = result.inserted_id
        return self._to_response(event_data)

    async def count_created_after(self,owner_id: str, after: datetime) -> int:
        search_id = UUID(owner_id) if isinstance(owner_id, str) else owner_id
        return await self.collection.count_documents({
            "owner_id": search_id,
            "created_at": {"$gte": after},
        })

    async def get_by_id(self, event_id: str):
        doc = await self.collection.find_one(
            {"_id": to_object_id(event_id)}
        )
        return self._to_response(doc) if doc else None

    async def list_by_owner(self, owner_id: UUID, limit: int,
                            last_created_at: datetime | None = None,
                            last_id: str | None = None) -> list[EventResponse]:
        search_id = UUID(owner_id) if isinstance(owner_id, str) else owner_id
        limit = min(limit, 100)

        query: dict = {"owner_id": search_id}

        if last_created_at and last_id:
            oid = to_object_id(last_id)

            query["$or"] = [
                {"created_at": {"$lt": last_created_at}},
                {
                    "created_at": last_created_at,
                    "_id": {"$lt": oid},
                },
            ]

        cursor = (
            self.collection.find(query)
            .sort([
                ("created_at", DESCENDING),
                ("_id", DESCENDING),
            ])
            .limit(limit)
        )

        return [self._to_response(doc) async for doc in cursor]
    
    async def delete(self, event_id: str):
        result = await self.collection.delete_one(
            {"_id": to_object_id(event_id)}
        )
        return result.deleted_count == 1

    async def update(self, event_id: str, update_data: EventUpdate) -> EventResponse | None:
        result = await self.collection.update_one(
            {"_id": to_object_id(event_id)},
            {"$set": update_data.model_dump(exclude_unset=True)},
        )
        if result.matched_count == 0:
            return None

        return await self.get_by_id(event_id)

        

    @staticmethod
    def _to_response(doc: dict) -> EventResponse:
        data = doc.copy()
        if "_id" in data:
            data["id"] = str(data.pop("_id"))

        if "owner_id" in data:
            data["owner_id"] = str(data["owner_id"])

        return EventResponse.model_validate(data)
