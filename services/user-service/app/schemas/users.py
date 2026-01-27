from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import UTC, datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    auth_role: str = "user"
    created_at: datetime = datetime.now(UTC)


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    email: EmailStr
    username: str
    auth_role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    


