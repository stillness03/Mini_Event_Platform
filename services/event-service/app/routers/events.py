from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.events import EventCreate, EventResponse, EventUpdate, UserContext
from app.repositories.event import EventRepository
from app.core.security import event_creation_rate_limit, get_event_repo, get_current_user

router = APIRouter(prefix="/events", tags=["Events"])


@router.post( "", response_model=EventResponse,
        status_code=status.HTTP_201_CREATED, dependencies=[Depends(event_creation_rate_limit)],
        )
async def create_event(
    event: EventCreate,
    repo: EventRepository = Depends(get_event_repo),
    user: UserContext = Depends(get_current_user),  # placeholder done in security.py(not forgotten)
):
    return await repo.create_event(event, user.owner_id)

@router.get("/my", response_model=list[EventResponse])
async def list_my_events(
    limit: int = 20,
    offset: int = 0,
    repo: EventRepository = Depends(get_event_repo),
    user: UserContext = Depends(get_current_user),
):
    return await repo.list_by_owner(
        owner_id=user.owner_id,
        limit=limit,
        offset=offset,
    )

@router.get( "/{event_id}", response_model=EventResponse)
async def get_event( event_id: str,
    repo: EventRepository = Depends(get_event_repo),
    ):
    event = await repo.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/{event_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: str,
    repo: EventRepository = Depends(get_event_repo),
    user: UserContext = Depends(get_current_user)
):
    success = await repo.delete_event(event_id, user)

    if not success:
        raise HTTPException(status_code=404, detail="Event not found")

    return None


@router.post("/{event_id}/update", response_model=EventResponse)
async def update_event(
    event_id: str,
    update_data: EventUpdate,
    repo: EventRepository = Depends(get_event_repo),
    user: UserContext = Depends(get_current_user),
):
    updated_event = await repo.update_event(
        event_id=event_id,
        update_data=update_data,
        user=user,
    )

    if not updated_event:
        raise HTTPException(status_code=404, detail="Event not found")

    return updated_event
