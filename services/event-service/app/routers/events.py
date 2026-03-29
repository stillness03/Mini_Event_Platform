from fastapi import APIRouter, Depends, HTTPException

from app.schemas.events import EventCreate, EventListResponse, EventResponse, EventUpdate
from app.core.security import event_creation_rate_limit
from app.core.dependencies import get_event_service, get_current_user
from app.service.event_service import EventService
from shared import UserContext

router = APIRouter(prefix="/events", tags=["Events"])


@router.post(
        "", response_model=EventResponse, status_code=201,
        dependencies=[Depends(event_creation_rate_limit)]
    )
async def create_event(
    event: EventCreate,
    current_user: UserContext = Depends(get_current_user),
    service: EventService = Depends(get_event_service),
):
    return await service.create_event(event, current_user)


@router.get("/my", response_model=EventListResponse)
async def list_my_events(
    limit: int = 20,
    cursor: str | None = None,
    user: UserContext = Depends(get_current_user),
    service: EventService = Depends(get_event_service),
):
    return await service.list_my_events(
        user=user,
        limit=limit,
        cursor=cursor,
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    service: EventService = Depends(get_event_service),
):
    event = await service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404)
    return event


@router.delete("/{event_id}")
async def delete_event(
    event_id: str,
    user: UserContext = Depends(get_current_user),
    service: EventService = Depends(get_event_service),
):
    success = await service.delete_event(event_id, user)
    if not success:
        raise HTTPException(status_code=404)
    return None


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    update: EventUpdate,
    user: UserContext = Depends(get_current_user),
    service: EventService = Depends(get_event_service),
):
    updated = await service.update_event(event_id, update, user)
    if not updated:
        raise HTTPException(status_code=404)
    return updated
