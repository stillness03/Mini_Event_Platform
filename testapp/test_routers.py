import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_read_events():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get("/events/all-events")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_event(test_user):
    assert test_user.id is not None

    event_data = {
        "title": "Test Event",
        "description": "This is a test event",
        "owner_id": test_user.id
    }

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/events/create-event",
            json=event_data
        )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Event"
    assert data["owner_id"] == test_user.id

