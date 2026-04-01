import pytest
from bson import ObjectId
from uuid import uuid4

from app.schemas.events import EventCreate, EventUpdate
from shared import UserContext

@pytest.mark.asyncio
async def test_update_event_permission_denied(event_repo, event_service):
    owner_id = uuid4()
    other_user = UserContext(
        user_id=str(uuid4()),
        role="user"
    )

    event = await event_repo.create_event(
        EventCreate(title="Secret", description="Hidden"),
        owner_id
    )

    with pytest.raises(PermissionError):
        await event_service.update_event(
            event.id, 
            EventUpdate(title="Hack"), 
            other_user
        )

@pytest.mark.asyncio
async def test_delete_event_permission_denied(event_repo, event_service):
    owner_id = uuid4()

    other_user = UserContext(
        user_id=str(uuid4()),
        role="user"
    )

    event = await event_repo.create_event(
        EventCreate(title="Secret", description="Hidden"),
        owner_id
    )

    with pytest.raises(PermissionError):
        await event_service.delete_event(event.id, other_user)

@pytest.mark.asyncio
async def test_admin_can_modify_any_event(event_repo, event_service):
    owner_id = uuid4()

    admin = UserContext(
        user_id=str(uuid4()),
        role="admin"
    )

    event = await event_repo.create_event(
        EventCreate(title="User Event", description="Owned"),
        owner_id
    )

    updated = await event_service.update_event(
        event.id, 
        EventUpdate(title="Admin Updated"), 
        admin
    )

    assert updated["title"] == "Admin Updated"


@pytest.mark.asyncio
async def test_update_event_partial(event_repo, event_service):
    owner_id = uuid4()

    user = UserContext(user_id=owner_id, role="user")

    event = await event_repo.create_event(
        EventCreate(title="Title", description="Desc"),
        owner_id
    )

    updated = await event_service.update_event(
        event.id, 
        EventUpdate(title="Only Title Changed"), 
        user
    )

    assert updated["title"] == "Only Title Changed"
    assert updated["description"] == "Desc"


@pytest.mark.asyncio
async def test_get_event_not_found(async_client):
    fake_id = str(ObjectId())

    res = await async_client.get(f"/events/{fake_id}")

    assert res.status_code == 404

@pytest.mark.asyncio
async def test_delete_event_not_found(async_client):
    fake_id = str(ObjectId())

    res = await async_client.delete(f"/events/{fake_id}")

    assert res.status_code == 404

@pytest.mark.asyncio
async def test_update_event_not_found(async_client):
    fake_id = str(ObjectId())

    res = await async_client.put(
        f"/events/{fake_id}", 
        json={"title": "New"}
        )

    assert res.status_code == 404
