import uuid
import enum
from sqlalchemy import text
from sqlalchemy import Column, Enum, String, DateTime, UniqueConstraint, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True),
                primary_key=True,
                index=True,
                default=uuid.uuid4,
                server_default=text("gen_random_uuid()")
                )

    event_id = Column(String, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone_number = Column(String(50))
    email = Column(String(255), index=True)

    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    currency = Column(String(3), server_default="UAH", nullable=False)

    status = Column(String, default=PaymentStatus.PENDING, nullable=False)

    ordering_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_user_event_payment"),
    )