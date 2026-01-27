from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

from datetime import UTC, datetime, timezone


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship(
        lambda: User,
        back_populates="events"
    )

    subscriptions = relationship(
        lambda: Subscription,
        back_populates="event"
    )


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    subscript_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    event = relationship(
        lambda: Event,
        back_populates="subscriptions"
    )

    user = relationship(
        lambda: User,
        back_populates="subscriptions"
    )
    
from app.models.users import User