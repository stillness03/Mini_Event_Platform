from pydantic import BaseModel, ConfigDict
from datetime import datetime


class EventCreate(BaseModel):
    title: str
    description: str


# ------------------- Response Schema -------------------
class EventResponse(BaseModel):
    id: int
    title: str
    description: str
    owner_id: int

    model_config = ConfigDict(from_attributes=True)


# ------------------- Subscription Response Schema -------------------
class SubscriptionResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    subscript_at: datetime

    model_config = ConfigDict(from_attributes=True)


