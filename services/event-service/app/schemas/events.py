from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from uuid import UUID

class EventBase(BaseModel):
    title: str
    description: str


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class EventResponse(EventBase):
    id: str
    owner_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    schema_version: int

class EventListResponse(BaseModel):
    items: List[EventResponse]
    next_cursor: Optional[str]

