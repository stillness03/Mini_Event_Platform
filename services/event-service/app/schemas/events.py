from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserContext(BaseModel):
    owner_id: str
    role: str


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
    owner_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    schema_version: int



