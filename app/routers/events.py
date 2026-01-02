from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session
from database import get_db

from app.schemas.events import EventCreate, EventResponse
from app.models.users import User
from app.routers.users import get_user_from_token, get_user_role
from app.models.events import Event, Subscription


router = APIRouter(prefix='/events', tags=['events'])


def check_create_event_permission(
    time_frame: timedelta,
    max_events: int
):
    def dependency(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_user_from_token),
    ):
        time_limit = datetime.now(timezone.utc) - time_frame

        event_count = db.query(Event).filter(
            Event.owner_id == current_user.id,
            Event.created_at >= time_limit
        ).count()

        if event_count >= max_events:
            raise HTTPException(
                status_code=400,
                detail="You have reached the maximum number of events you can create in this time period."
            )
    return dependency

    

@router.post("/create-admin_event", response_model=EventResponse)
async def create_events(
    event_model: EventCreate,
    db: Session = Depends(get_db),
    role: str = Depends(get_user_role),
    current_user: User = Depends(get_user_from_token)
):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create events")

    new_event = Event(
        title=event_model.title,
        description=event_model.description,
        owner_id=current_user.id
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event


@router.post(
    "/create-event",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_create_event_permission(
        time_frame=timedelta(minutes=1),
        max_events=5
    ))]
)
async def create_event(
    event_model: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_token),
):
    new_event = Event(
        title=event_model.title,
        description=event_model.description,
        owner_id=current_user.id
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event


@router.get("/my-events", response_model=list[EventResponse])
async def get_my_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_token)
):
    events = db.query(Event).filter(Event.owner_id == current_user.id).all()
    return events

@router.post("subscribe/{event_id}", status_code=status.HTTP_201_CREATED)
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
    subscriptions = db.query(Subscription).filter(Subscription.user_id == current_user.id).all()
    events = [db.query(Event).filter(Event.id == sub.event_id).first() for sub in subscriptions]
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

@router.get("/all-events", response_model=list[EventResponse])
async def get_all_events(
    db: Session = Depends(get_db)
):
    events = db.query(Event).all()
    return events

