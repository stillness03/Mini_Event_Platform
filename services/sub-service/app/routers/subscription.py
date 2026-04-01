import logging
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from shared import UserContext

from app.core.database import get_db
from app.core.security import get_current_user
from app.service.sub_service import SubscriptionService
from app.repositories.sub_repository import SubRepository
from app.clients.event_client import (
    EventClient,
    get_event_client,
)


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/sub", tags=["subscriptions"])


def get_subscription_service(
    db: Session = Depends(get_db),
    event_client: EventClient = Depends(get_event_client),
)-> SubscriptionService:
    repo = SubRepository(db)
    service = SubscriptionService(repo, event_client)
    return service


@router.post("/subscribe/{event_id}", status_code=status.HTTP_201_CREATED)
async def subscribe_to_event(
    event_id: str,
    current_user: UserContext = Depends(get_current_user),
    service: SubscriptionService = Depends(get_subscription_service),
):
    return await service.subscribe(event_id, current_user.user_id)


@router.get("/my-subscriptions")
async def get_my_subscriptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: UserContext = Depends(get_current_user),
    service: SubscriptionService = Depends(get_subscription_service),
):
   return await service.list_user_subscriptions(
        current_user.user_id,
        page, page_size)


@router.post("/unsubscribe/{event_id}")
async def unsubscribe_from_event(
    event_id: str,
    current_user: UserContext = Depends(get_current_user),
    service: SubscriptionService = Depends(get_subscription_service),
):
    return await service.unsubscribe(event_id, current_user.user_id)