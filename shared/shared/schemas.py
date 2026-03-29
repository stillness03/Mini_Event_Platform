from pydantic import BaseModel
from uuid import UUID

class UserContext(BaseModel):
    user_id: UUID
    role: str = "user"