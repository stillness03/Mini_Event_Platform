from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from datetime import datetime
from uuid import UUID


# --- Base ---

class UserBase(BaseModel):
    username: str
    email: EmailStr


# --- Create ---

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)
    password_confirm: str

    @model_validator(mode="after")
    def passwords_match(self) -> "UserCreate":
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


# --- Update ---

class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=72)


# --- Response ---

class UserResponse(UserBase):
    id: UUID
    auth_role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class SessionResponse(BaseModel):
    id: int
    user_agent: str | None
    ip_address: str | None
    created_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Login ---

class LoginRequest(BaseModel):
    email: EmailStr
    password: str