import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.subcription import UserContext
from app.models.subscription import Subscription

from app.clients.event_client import (
    EventClient,
    get_event_client,
    EventServiceUnavailable,
)


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/events", tags=["subscriptions"])


def paginate(items, page: int = 1, page_size: int = 10):
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end]


@router.post("/subscribe/{event_id}", status_code=status.HTTP_201_CREATED)
async def subscribe_to_event(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    event_client: EventClient = Depends(get_event_client),
):
    
    try:
        event = await event_client.get_event(event_id)
    except EventServiceUnavailable:
        logger.warning(
            "event_service_unavailable user_id=%s event_id=%s",
            current_user.user_id,
            event_id,
        )
        raise HTTPException(503, "Event service unavailable")

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event["owner_id"] == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot subscribe to your own event",
        )
    
    existing_subscription = db.query(Subscription).filter(
        Subscription.event_id == event_id,
        Subscription.user_id == current_user.user_id,
    ).first()

    if existing_subscription:
        logger.info(
            "subscription_already_exists user_id=%s event_id=%s",
            current_user.user_id,
            event_id,
        )
        return {"message": "Already subscribed"}
    
    new_subscription = Subscription(
        event_id=event_id,
        user_id=current_user.user_id
    )

    try:
        db.add(new_subscription)
        db.commit()
        db.refresh(new_subscription)

        logger.info(
            "subscription_created user_id=%s event_id=%s",
            current_user.user_id,
            event_id,
        )

    except Exception:
        db.rollback()
        logger.exception(
            "subscription_creation_failed user_id=%s event_id=%s",
            current_user.user_id,
            event_id,
        )
        raise HTTPException(500, "Subscription failed")

    return {"message": "Subscribed successfully"}


@router.get("/my-subscriptions")
async def get_my_subscriptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    event_client: EventClient = Depends(get_event_client),
):
    total = db.query(Subscription).filter(
        Subscription.user_id == current_user.user_id
    ).count()

    offset = (page - 1) * page_size

    subscriptions = (
        db.query(Subscription)
        .filter(Subscription.user_id == current_user.user_id)
        .offset(offset)
        .limit(page_size)
        .all()
    )

    if not subscriptions:
        return {
            "items": [],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    event_ids = [s.event_id for s in subscriptions]

    try:
        events = await event_client.get_events_batch(event_ids)
    except EventServiceUnavailable:
        logger.warning(
            "event_service_batch_unavailable user_id=%s",
            current_user.user_id,
        )
        raise HTTPException(503, "Event service unavailable")

    return {
        "items": events,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/unsubscribe/{event_id}")
async def unsubscribe_from_event(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    subscription = db.query(Subscription).filter(
        Subscription.event_id == event_id,
        Subscription.user_id == current_user.user_id,
    ).first()

    if not subscription:
        raise HTTPException(404, "Subscription not found")

    try:
        db.delete(subscription)
        db.commit()

        logger.info(
            "User %s unsubscribed from event %s",
            current_user.user_id,
            event_id,
        )

    except Exception:
        db.rollback()
        logger.exception(
            "unsubscribe_failed user_id=%s event_id=%s",
            current_user.user_id,
            event_id,
        )
        raise HTTPException(500, "Unsubscribe failed")

    return {"message": "Unsubscribed successfully"}


