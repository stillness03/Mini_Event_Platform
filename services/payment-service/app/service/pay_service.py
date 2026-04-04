import logging
from uuid import UUID
from fastapi import HTTPException, status

from app.repositories.payments_rep import PaymentRepository
from app.clients.event_client import EventClient, EventServiceUnavailable
from app.schemas.payments import PaymentRequest

logger = logging.getLogger(__name__)


class PaymentService:
    def __init__(self, repo: PaymentRepository, event_client: EventClient):
        self.repo = repo
        self.event_client = event_client

    async def create_payment(self, data: PaymentRequest) -> dict:
        try:
            event = await self.event_client.get_event(data.event_id)
        except EventServiceUnavailable:
            logger.warning(
                "event_service_unavailable user_id=%s event_id=%s",
                data.user_id, data.event_id
            )
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "Event service unavailable"
            )

        if not event:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Event not found"
            )

        if event.get("owner_id") == str(data.user_id):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="You cannot subscribe to your own event"
            )

        existing = self.repo.get_by_event_and_user(data.event_id, data.user_id)
        if existing:
            if existing.status == "success":
                return {"message": "Already subscribed and paid"}
            return {"message": "Payment pending", "payment_id": existing.id}

        try:
            pay = self.repo.create(data)
            return {
                "message": "Payment record created",
                "payment_id": pay.id,
                "amount": pay.amount
            }
        except Exception as e:
            logger.error(
                "payment_creation_failed error=%s",
                str(e))
            self.repo.rollback()
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Failed to create payment"
            )

    async def list_user_payments(self, user_id: UUID,
                                 page: int, page_size: int) -> dict:
        offset = (page - 1) * page_size
        payments = self.repo.list_user_ordered(user_id, offset, page_size)

        total = self.repo.count_by_user(user_id)

        return {
            "items": payments,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
