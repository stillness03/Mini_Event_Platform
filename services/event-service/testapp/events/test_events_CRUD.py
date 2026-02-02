import pytest
from bson import ObjectId
from datetime import datetime, timezone, timedelta


from app.schemas.events import EventCreate, EventUpdate, UserContext


@pytest.mark.asyncio
async def test_event_rate_limit(async_client):
    for i in range(5):
        response = await async_client.post("/events", json={"title": f"Event {i}", "description": "Desc"})
        assert response.status_code == 201

  
    response = await async_client.post("/events", json={"title": "Event 6", "description": "Desc"})
    assert response.status_code == 429



@pytest.mark.asyncio
async def test_get_event_not_found(async_client):
    fake_id = str(ObjectId())

    res = await async_client.get(f"/events/{fake_id}")

    assert res.status_code == 404



@pytest.mark.asyncio
async def test_delete_event_not_found(async_client):
    fake_id = str(ObjectId())

    res = await async_client.post(f"/events/{fake_id}/delete")

    assert res.status_code == 404



@pytest.mark.asyncio
async def test_update_event_not_found(async_client):
    fake_id = str(ObjectId())

    res = await async_client.post(
        f"/events/{fake_id}/update",
        json={"title": "New"}
    )

    assert res.status_code == 404


@pytest.mark.asyncio
async def test_update_event_permission_denied(event_repo):
    owner_id = str(ObjectId())
    other_user = UserContext(
        owner_id=str(ObjectId()),
        role="user"
    )

    event = await event_repo.create_event(
        EventCreate(title="Secret", description="Hidden"),
        owner_id
    )

    with pytest.raises(PermissionError):
        await event_repo.update_event(
            event.id,
            EventUpdate(title="Hack"),
            other_user
        )


@pytest.mark.asyncio
async def test_delete_event_permission_denied(event_repo):
    owner_id = str(ObjectId())

    other_user = UserContext(
        owner_id=str(ObjectId()),
        role="user"
    )

    event = await event_repo.create_event(
        EventCreate(title="Secret", description="Hidden"),
        owner_id
    )

    with pytest.raises(PermissionError):
        await event_repo.delete_event(event.id, other_user)


@pytest.mark.asyncio
async def test_admin_can_modify_any_event(event_repo):
    owner_id = str(ObjectId())

    admin = UserContext(
        owner_id=str(ObjectId()),
        role="admin"
    )

    event = await event_repo.create_event(
        EventCreate(title="User Event", description="Owned"),
        owner_id
    )

    updated = await event_repo.update_event(
        event.id,
        EventUpdate(title="Admin Updated"),
        admin
    )

    assert updated.title == "Admin Updated"


@pytest.mark.asyncio
async def test_update_event_partial(event_repo):
    owner_id = str(ObjectId())

    user = UserContext(owner_id=owner_id, role="user")

    event = await event_repo.create_event(
        EventCreate(title="Title", description="Desc"),
        owner_id
    )

    updated = await event_repo.update_event(
        event.id,
        EventUpdate(title="Only Title Changed"),
        user
    )

    assert updated.title == "Only Title Changed"
    assert updated.description == "Desc"


@pytest.mark.asyncio
async def test_list_events_sorted_desc(event_repo):
    owner_id = str(ObjectId())

    await event_repo.create_event(
        EventCreate(title="Old", description="1"),
        owner_id
    )

    await event_repo.create_event(
        EventCreate(title="New", description="2"),
        owner_id
    )

    events = await event_repo.list_by_owner(owner_id)

    assert events[0].title == "New"
    assert events[1].title == "Old"


@pytest.mark.asyncio
async def test_count_created_after(event_repo):
    owner_id = str(ObjectId())

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