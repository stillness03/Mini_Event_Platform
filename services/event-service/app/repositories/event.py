from bson import ObjectId
from datetime import datetime, timezone

from pymongo import ReturnDocument

from app.repositories.base import BaseRepository
from app.schemas.events import EventCreate, EventResponse, EventUpdate, UserContext
from app.models.mongo import to_object_id
from app.core.policies.event import EventPolicy

class EventRepository(BaseRepository):
    collection_name = "events"

    async def create_event(
            self, event_data: EventCreate,
            owner_id: str) -> EventResponse:
        event_data = {
            "title": event_data.title,
            "description": event_data.description,
            "owner_id": to_object_id(owner_id),
            "created_at": datetime.now(timezone.utc),
            "schema_version": 2, # for future migrations
        }

        result = await self.collection.insert_one(event_data)
        event_data["_id"] = result.inserted_id

        return self._to_response(event_data)
    

    async def count_created_after(self, owner_id: str, after: datetime) -> int:
        return await self.collection.count_documents({
            "owner_id": to_object_id(owner_id),
            "created_at": {"$gte": after},
        })


    async def get_event_by_id(self, event_id: str) -> EventResponse | None:
        event_data = await self.collection.find_one(
            {"_id": to_object_id(event_id)}
        )
        if not event_data:
            return None
        return self._to_response(event_data)


    async def list_by_owner(self, owner_id: str,
                            limit: int = 20, offset: int = 0
                            ) -> list[EventResponse]:
        cursor = (
            self.collection.find(
                {"owner_id": to_object_id(owner_id)}
                ).sort("created_at", -1)
                 .skip(offset)
                 .limit(limit)
            )
        return [self._to_response(doc) async for doc in cursor]
    
    async def delete_event(self, event_id: str, user: UserContext) -> bool:
        event = await self.collection.find_one({"_id": ObjectId(event_id)})
        if not event:
            return False

        if not EventPolicy.can_modify(event, user):
            raise PermissionError("Not allowed")

        result = await self.collection.delete_one(
            {"_id": ObjectId(event_id)}
        )
        return result.deleted_count == 1
    

    async def update_event(self, event_id: str,
        update_data: EventUpdate, user: UserContext,
    ):
        event = await self.collection.find_one({"_id": ObjectId(event_id)})
        if not event:
            return None

        if not EventPolicy.can_modify(event, user):
            raise PermissionError("Not allowed")

        await self.collection.update_one(
             {"_id": ObjectId(event_id)},
            {"$set": update_data.model_dump(exclude_unset=True)},
        )

        return await self.get_event_by_id(event_id)

    @staticmethod
    def _to_response(event_data: dict) -> EventResponse:
        data = event_data.copy()
        data["id"] = str(data.pop("_id"))
        data["owner_id"] = str(data.get("owner_id"))
        return EventResponse.model_validate(data)