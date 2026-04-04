import uuid
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


from app.models.payment import PaymentStatus


class PaymentRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    user_id: uuid.UUID
    amount: Decimal = Field(gt=0, decimal_places=2)
    first_name: str
    last_name: str
    email: str
    phone_number: str | None = None

class PaymentResponse(PaymentRequest):
    id: uuid.UUID
    status: str
    ordering_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)