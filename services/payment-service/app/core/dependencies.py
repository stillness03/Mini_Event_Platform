import httpx
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.repositories.payments_rep import PaymentRepository
from app.repositories.stripe_gateway import StripeGateway
from app.client.event_client import EventClient
from app.service.pay_service import PaymentService

settings = get_settings()

http_client = httpx.AsyncClient()

stripe_gateway = StripeGateway(api_key=settings.STRIPE_SECRET_KEY)
event_client = EventClient(http_client=http_client)

async def get_payment_service(db: AsyncSession = Depends(get_db)) -> PaymentService:
    repo = PaymentRepository(db)

    return PaymentService(
        repo=repo,
        event_client=event_client,
        stripe_gateway=stripe_gateway
    )





