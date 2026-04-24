from fastapi import APIRouter, Depends, Header, Request, HTTPException
from app.service.pay_service import PaymentService
from app.core.dependencies import get_payment_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(
        request: Request,
        stripe_signature: str = Header(None),
        service: PaymentService = Depends(get_payment_service)
):
    payload = await request.body()

    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature")

    try:
        event = service.stripe_gateway.verify_webhook(payload, stripe_signature)
    except Exception as e:
        logger.error("webhook_verification_failed: %s", str(e))
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        stripe_id = session.id

        await service.confirm_payment(stripe_id)

    return {"status": "success"}