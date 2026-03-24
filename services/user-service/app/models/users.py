from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import UTC, datetime
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    auth_role = Column(String, default="user", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
