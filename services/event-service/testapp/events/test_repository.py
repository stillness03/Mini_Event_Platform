import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from app.schemas.events import EventCreate

@pytest.mark.asyncio
async def test_create_and_get_event(event_repo):
    owner_id = uuid4()
    event_in = EventCreate(title="Test Event", description="Test Description")


    event = await event_repo.create_event(event_in, owner_id)
    assert event.title == "Test Event"
    assert event.description == "Test Description"
    assert event.owner_id == owner_id
    assert event.id is not None


    fetched = await event_repo.get_by_id(event.id)
    assert fetched is not None
    assert fetched.title == "Test Event"
    assert fetched.description == "Test Description"


@pytest.mark.asyncio
async def test_list_events_sorted_desc(event_repo):
    owner_id = uuid4()
    print(f"\nDEBUG: Searching for owner_id: {owner_id} (type: {type(owner_id)})")

    await event_repo.create_event(
        EventCreate(title="Old", description="1"),
        owner_id
    )

    await event_repo.create_event(
        EventCreate(title="New", description="2"),
        owner_id
    )

    events = await event_repo.list_by_owner(owner_id, limit=10)
    print(f"DEBUG: Found events: {len(events)}")
    assert events[0].title == "New"
    assert events[1].title == "Old"


@pytest.mark.asyncio
async def test_count_created_after(event_repo):
    owner_id = uuid4()

    now = datetime.now(timezone.utc)

    await event_repo.create_event(
        EventCreate(title="Event1", description=""),
        owner_id
    )

    count = await event_repo.count_created_after(
        owner_id,
        now - timedelta(minutes=1)
    )

    assert count >= 1
