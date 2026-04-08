from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from sqlalchemy import exists, and_

from app.models.payments import Payment
from app.schemas.payments import PaymentRequest, PaymentResponse
from .base import BaseRepository


class PaymentRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, payment: PaymentRequest) -> Payment:
        data = Payment(
            first_name=payment.first_name,
            last_name=payment.last_name,
            email=payment.email,
            phone_number=payment.phone_number,
            event_id=payment.event_id,
            user_id=payment.user_id,
            amount=payment.amount,
        )
        self.db.add(data)
        self.flush()
        return data


    def get_by_event_and_user(self, event_id: str, user_id: UUID) -> Optional[Payment]:
        return (
            self.db.query(Payment)
            .filter(Payment.event_id == event_id, Payment.user_id == user_id)
            .first()
        )


    def list_user_ordered(self, user_id: UUID, offset: int = 0, limit: int = 10) -> List[Payment]:
        return (
            self.db.query(Payment)
            .filter(Payment.user_id == user_id)
            .order_by(Payment.ordering_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )


    def update_status(self, payment_id: UUID, status: str) -> Optional[Payment]:
        db_payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if db_payment:
            db_payment.status = status
            self.flush()
            self.refresh(db_payment)
        return db_payment


    def get_locked(self, payment_id: UUID) -> Optional[Payment]:
        """Receives the payment and locks it in the database until the transaction is complete"""
        return (
            self.db.query(Payment)
            .filter(Payment.id == payment_id)
            .with_for_update()
            .first()
        )

    def exists(self, event_id: str, user_id: UUID) -> bool:
        return self.db.query(
            exists().where(and_(
                Payment.event_id == event_id,
                Payment.user_id == user_id
            )
            )
        ).scalar()

    def count_by_user(self, user_id: UUID) -> int:
        return self.db.query(Payment).filter(Payment.user_id == user_id).count()
