from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
from sqlalchemy import select, and_, func, exists

from app.models.payments import Payment, PaymentStatus
from app.schemas.payments import PaymentRequest
from .base import BaseRepository


class PaymentRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def create(self, payment: PaymentRequest) -> Payment:
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
        await self.flush()
        return data


    async def get_by_event_and_user(self, event_id: str, user_id: UUID) -> Optional[Payment]:
        query = select(Payment).where(
            and_(Payment.event_id == event_id, Payment.user_id == user_id)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_stripe_id(self, stripe_id: str) -> Optional[Payment]:
        query = select(Payment).where(Payment.stripe_id == stripe_id)
        result = await self.db.execute(query)
        return result.scalars().first()


    async def list_user_ordered(self, user_id: UUID, offset: int = 0, limit: int = 10) -> List[Payment]:
        query = (
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.ordering_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())


    async def update_stripe_id(self, stripe_id: str, payment_id: UUID) -> Optional[Payment]:
        query = select(Payment).where(Payment.id == payment_id)
        result = await self.db.execute(query)
        db_payment = result.scalars().first()
        
        if db_payment:
            db_payment.stripe_id = stripe_id
            await self.flush()
            await self.db.refresh(db_payment)
        return db_payment


    async def update_status(self, payment_id: UUID, status: str) -> Optional[Payment]:
        query = select(Payment).where(Payment.id == payment_id)
        result = await self.db.execute(query)
        db_payment = result.scalars().first()
        
        if db_payment:
            db_payment.status = status
            await self.flush()
            await self.db.refresh(db_payment)
        return db_payment


    async def get_locked(self, payment_id: UUID) -> Optional[Payment]:
        query = (
            select(Payment)
            .where(Payment.id == payment_id)
            .with_for_update()
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def exists(self, event_id: str, user_id: UUID) -> bool:
        query = select(
            exists().where(
                and_(
                    Payment.event_id == event_id,
                    Payment.user_id == user_id
                )
            )
        )
        result = await self.db.execute(query)
        return bool(result.scalar())

    async def count_by_user(self, user_id: UUID) -> int:
        query = select(func.count()).select_from(Payment).where(Payment.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def update_after_stripe(
        self,
        payment_id: UUID,
        stripe_id: str,
        checkout_url: str,
        status: PaymentStatus,
    ) -> Optional[Payment]:
        query = select(Payment).where(Payment.id == payment_id)
        result = await self.db.execute(query)
        db_payment = result.scalars().first()

        if db_payment:
            db_payment.stripe_id = stripe_id
            db_payment.checkout_url = checkout_url
            db_payment.status = status
            await self.flush()
            await self.db.refresh(db_payment)
        return db_payment
