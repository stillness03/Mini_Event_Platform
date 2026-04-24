from __future__ import annotations

import logging
import asyncio
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from functools import partial
from typing import Any
from math import ceil

from app.repositories.payments_rep import PaymentRepository
from app.models.payments import PaymentStatus
from app.repositories.stripe_gateway import StripeGateway
from app.client.event_client import EventClient, EventServiceUnavailable
from app.schemas.payments import PaymentRequest, PaymentResponse

logger = logging.getLogger(__name__)

STRIPE_TIMEOUT_SEC = 5
EVENT_TIMEOUT_SEC = 3


class PaymentService:
    def __init__(
            self,
            repo: PaymentRepository,
            event_client: EventClient,
            stripe_gateway: StripeGateway
    ):
        self.repo = repo
        self.event_client = event_client
        self.stripe_gateway = stripe_gateway

    async def create_payment(self, data: PaymentRequest) -> dict:
        event = await self._fetch_event(data)
        self._validate_event(event, data.user_id)

        if existing := await self.repo.get_by_event_and_user(data.event_id, data.user_id):
            return self._existing_payment_response(existing)

        pay = await self._create_payment_record(data)
        checkout_session = await self._create_stripe_session(pay)
        return await self._finalize_payment(pay, checkout_session)


    async def _fetch_event(self, data: PaymentRequest) -> dict:
        try:
            return await asyncio.wait_for(
                self.event_client.get_event(data.event_id),
                timeout=EVENT_TIMEOUT_SEC,
            )
        except asyncio.TimeoutError:
            logger.warning("event_service_timeout user_id=%s event_id=%s", data.user_id, data.event_id)
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Event service timeout")
        except EventServiceUnavailable:
            logger.warning("event_service_unavailable user_id=%s event_id=%s", data.user_id, data.event_id)
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Event service unavailable")


    def _validate_event(self, event: dict | None, user_id: UUID) -> None:
        if not event:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")
        if event.get("owner_id") == str(user_id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You cannot subscribe to your own event")


    def _existing_payment_response(self, existing) -> dict:
        if existing.status == PaymentStatus.SUCCESS:
            return {"message": "Already paid", "payment_id": existing.id}
        return {
            "message": "Payment already initiated",
            "payment_id": existing.id,
            "checkout_url": existing.checkout_url,
            "status": existing.status,
        }


    async def _create_payment_record(self, data: PaymentRequest):
        try:
            pay = await self.repo.create(data)
            await self.repo.commit()
            return pay
        except IntegrityError:
            await self.repo.rollback()
            existing = await self.repo.get_by_event_and_user(data.event_id, data.user_id)
            if existing:
                return self._existing_payment_response(existing)  # type: ignore[return-value]
            raise HTTPException(status.HTTP_409_CONFLICT, "Payment already exists")


    async def _create_stripe_session(self, pay):
        try:
            func = partial(
                self.stripe_gateway.create_checkout_session,
                amount=int(pay.amount * 100),
                currency=pay.currency,
                payment_id=str(pay.id),
                email=pay.email,
            )
            return await asyncio.wait_for(
                asyncio.get_running_loop().run_in_executor(None, func),
                timeout=STRIPE_TIMEOUT_SEC,
            )
        except Exception as e:
            is_timeout = isinstance(e, asyncio.TimeoutError)
            logger.warning("stripe_timeout payment_id=%s", pay.id) if is_timeout else logger.exception("stripe_error payment_id=%s", pay.id)
            await self._safe_update_status(pay.id, PaymentStatus.FAILED)
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE if is_timeout else status.HTTP_502_BAD_GATEWAY,
                "Payment provider timeout" if is_timeout else "Payment provider error",
            )


    async def _finalize_payment(self, pay, checkout_session) -> dict:
        try:
            await self.repo.update_after_stripe(
                payment_id=pay.id,
                stripe_id=checkout_session.id,
                checkout_url=checkout_session.url,
                status=PaymentStatus.REQUIRES_PAYMENT,
            )
            await self.repo.commit()
        except Exception:
            logger.exception("failed_to_update_after_stripe payment_id=%s", pay.id)
            await self._safe_update_status(pay.id, PaymentStatus.FAILED)
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to finalize payment")

        return {
            "message": "Payment created",
            "payment_id": pay.id,
            "checkout_url": checkout_session.url,
        }


    async def _safe_update_status(self, payment_id, status: PaymentStatus) -> None:
        try:
            await self.repo.update_status(payment_id, status)
            await self.repo.commit()
        except Exception:
            logger.exception("failed_to_update_status payment_id=%s", payment_id)




    async def list_user_payments(self, user_id: UUID,
                                 page: int, page_size: int) -> dict[str, Any]:

        offset = (page - 1) * page_size

        payments = await self.repo.list_user_ordered(
            user_id, offset, page_size
        )
        total = await self.repo.count_by_user(user_id)

        return {
            "items": [PaymentResponse.model_validate(p) for p in payments],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": ceil(total / page_size) if total and page_size else 0,
        }

    async def confirm_payment(self, stripe_id: str) -> None:
        payment = await self.repo.get_by_stripe_id(stripe_id)

        if not payment:
            logger.error("payment_not_found_for_stripe_id: %s", stripe_id)
            return

        if payment.status == PaymentStatus.SUCCESS:
            logger.info("payment_already_confirmed: %s", payment.id)
            return

        await self.repo.update_status(payment.id, PaymentStatus.SUCCESS)
        await self.repo.commit()
        logger.info("payment_confirmed_successfully: %s", payment.id)