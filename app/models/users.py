from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    auth_role = Column(String, default="user")
    created_at = Column(DateTime, default=datetime.utcnow)

    events = relationship(
        lambda: Event,
        back_populates="owner"
    )

    subscriptions = relationship(
        lambda: Subscription,
        back_populates="user"
    )

from app.models.events import Event, Subscription