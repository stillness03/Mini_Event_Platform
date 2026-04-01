from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SubscriptionResponse(BaseModel):
    id: int
    event_id: str
    user_id: str
    subscript_at: datetime

    model_config = ConfigDict(from_attributes=True)

