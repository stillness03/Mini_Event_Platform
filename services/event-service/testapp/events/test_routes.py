import pytest


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

    assert isinstance(data["items"], list)
    assert len(data["items"]) >= 1
    assert data["items"][0]["title"] == "My Event"


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

    res = await async_client.delete(f"/events/{event_id}")
    assert res.status_code == 200

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

    res = await async_client.put(
        f"/events/{event_id}", 
        json=update_payload
    )

    assert res.status_code == 200
    data = res.json()

    assert data["title"] == "New Title"
    assert data["description"] == "Old Desc"


@pytest.mark.asyncio
async def test_event_rate_limit(async_client):
    for i in range(5):
        response = await async_client.post("/events", json={"title": f"Event {i}", "description": "Desc"})
        assert response.status_code == 201


    response = await async_client.post("/events", json={"title": "Event 6", "description": "Desc"})
    assert response.status_code == 429