from pydantic import BaseModel, ConfigDict
from datetime import datetime


class UserContext(BaseModel):
    user_id: str
    role: str


class SubscriptionResponse(BaseModel):
    id: int
    event_id: int
    user_id: str
    subscript_at: datetime

    model_config = ConfigDict(from_attributes=True)

