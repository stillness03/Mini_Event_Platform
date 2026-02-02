from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session
from database import get_db

from app.schemas.events import EventResponse
from app.models.users import User
from app.routers.users import get_user_from_token
from app.models.events import Event, Subscription


router = APIRouter(prefix='/events', tags=['events'])



@router.post("/subscribe/{event_id}", status_code=status.HTTP_201_CREATED)
async def subscribe_to_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_token)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")


    existing_subscription = db.query(Subscription).filter(
        Subscription.event_id == event_id,
        Subscription.user_id == current_user.id
    ).first()

    if current_user.id == event.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot subscribe to your own event",
        )

    if existing_subscription:
        raise HTTPException(status_code=400, detail="Already subscribed to this event")

    new_subscription = Subscription(
        event_id=event_id,
        user_id=current_user.id
    )
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)

    return {"message": "Subscribed successfully"}

@router.get("/my-subscriptions", response_model=list[EventResponse])
async def get_my_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_token)
):
    events = (
    db.query(Event)
    .join(Subscription, Subscription.event_id == Event.id)
    .filter(
        Subscription.user_id == current_user.id,
        Event.owner_id != current_user.id  # Exclude events owned by the user
    )
    .all()
    )
    return events

@router.post("/unsubscribe/{event_id}", status_code=status.HTTP_200_OK)
async def unsubscribe_from_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_token)
):
    subscription = db.query(Subscription).filter(
        Subscription.event_id == event_id,
        Subscription.user_id == current_user.id
    ).first()

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    db.delete(subscription)
    db.commit()

    return {"message": "Unsubscribed successfully"}


