from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base
from datetime import UTC, datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    auth_role = Column(String, default="user")
    created_at = Column(DateTime, default=datetime.now(UTC))
