from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from app.core.database import Base

from datetime import datetime, timezone



class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)

    event_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)

    subscript_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint("user_id", "event_id"),
    )
