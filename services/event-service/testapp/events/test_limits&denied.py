import pytest
from bson import ObjectId

from app.schemas.events import EventCreate


@pytest.mark.asyncio
async def test_create_and_get_event(event_repo):
    owner_id = str(ObjectId())
    event_in = EventCreate(title="Test Event", description="Test Description")


    event = await event_repo.create_event(event_in, owner_id)
    assert event.title == "Test Event"
    assert event.description == "Test Description"
    assert event.owner_id == owner_id
    assert event.id is not None


    fetched = await event_repo.get_event_by_id(event.id)
    assert fetched is not None
    assert fetched.title == "Test Event"
    assert fetched.description == "Test Description"


@pytest.mark.asyncio
async def test_create_event_route(async_client):
    payload = {
        "title": "Route Event",
        "description": "Route Description"
    }

    res = await async_client.post("/events", json=payload)

    assert res.status_code == 201
    data = res.json()

    assert data["title"] == "Route Event"
    assert data["description"] == "Route Description"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_my_events_route(async_client):
    payload = {
        "title": "My Event",
        "description": "Mine"
    }

    await async_client.post("/events", json=payload)

    res = await async_client.get("/events/my")

    assert res.status_code == 200
    data = res.json()

    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["title"] == "My Event"


@pytest.mark.asyncio
async def test_get_event_route(async_client):
    payload = {
        "title": "Get Event",
        "description": "Get Desc"
    }

    create_res = await async_client.post("/events", json=payload)
    event_id = create_res.json()["id"]

    res = await async_client.get(f"/events/{event_id}")

    assert res.status_code == 200
    assert res.json()["id"] == event_id


@pytest.mark.asyncio
async def test_delete_event_route(async_client):
    payload = {
        "title": "Delete Event",
        "description": "Delete Desc"
    }

    create_res = await async_client.post("/events", json=payload)
    event_id = create_res.json()["id"]

    res = await async_client.post(f"/events/{event_id}/delete")

    assert res.status_code == 204

    # verify deleted
    get_res = await async_client.get(f"/events/{event_id}")
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_update_event_route(async_client):
    payload = {
        "title": "Old Title",
        "description": "Old Desc"
    }

    create_res = await async_client.post("/events", json=payload)
    event_id = create_res.json()["id"]

    update_payload = {
        "title": "New Title"
    }

    res = await async_client.post(
        f"/events/{event_id}/update",
        json=update_payload
    )

    assert res.status_code == 200
    data = res.json()

    assert data["title"] == "New Title"
    assert data["description"] == "Old Desc"

