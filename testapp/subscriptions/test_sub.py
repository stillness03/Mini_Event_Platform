import pytest 

@pytest.mark.asyncio
async def test_subscribe_to_event(make_auth_client, test_user, test_user_2):

    # user1
    async for client1 in make_auth_client(test_user):
        event_data = {
            "title": "Subscription Event",
            "description": "Test",
        }
        response = await client1.post("/events/create-event", json=event_data)
        assert response.status_code == 201
        event_id = response.json()["id"]

    # user2
    async for client2 in make_auth_client(test_user_2):
        subscribe_response = await client2.post(f"/events/subscribe/{event_id}")
        assert subscribe_response.status_code == 201
        assert subscribe_response.json()["message"] == "Subscribed successfully"

@pytest.mark.asyncio
async def test_repeat_subscription(make_auth_client, test_user, test_user_2):
    # user1 creates event
    async for client1 in make_auth_client(test_user):
        response = await client1.post(
            "/events/create-event",
            json={"title": "Event", "description": "Test"}
        )
        assert response.status_code == 201
        event_id = response.json()["id"]

    # user2 subscribes first time
    async for client2 in make_auth_client(test_user_2):
        response = await client2.post(f"/events/subscribe/{event_id}")
        assert response.status_code == 201

        # user2 subscribes second time
        response = await client2.post(f"/events/subscribe/{event_id}")
        assert response.status_code == 400
        assert response.json()["detail"] == "Already subscribed to this event"

@pytest.mark.asyncio
async def test_subscribe_to_nonexistent_event(make_auth_client, test_user):
    async for client in make_auth_client(test_user):
        response = await client.post("/events/subscribe/999999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Event not found"

@pytest.mark.asyncio
async def test_get_my_subscriptions(make_auth_client, test_user, test_user_2):
    # user1 creates event
    async for client1 in make_auth_client(test_user):
        response = await client1.post(
            "/events/create-event",
            json={"title": "Sub Event", "description": "Test"}
        )
        event_id = response.json()["id"]

    # user2 subscribes
    async for client2 in make_auth_client(test_user_2):
        response = await client2.post(f"/events/subscribe/{event_id}")
        assert response.status_code == 201

        response = await client2.get("/events/my-subscriptions")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == event_id
        assert data[0]["title"] == "Sub Event"

@pytest.mark.asyncio
async def test_unsubscribe_from_event(make_auth_client, test_user, test_user_2):
    # user1 creates event
    async for client1 in make_auth_client(test_user):
        response = await client1.post(
            "/events/create-event",
            json={"title": "Unsub Event", "description": "Test"}
        )
        event_id = response.json()["id"]

    # user2 subscribes
    async for client2 in make_auth_client(test_user_2):
        response = await client2.post(f"/events/subscribe/{event_id}")
        assert response.status_code == 201

        # unsubscribe
        response = await client2.post(f"/events/unsubscribe/{event_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Unsubscribed successfully"

        # check subscriptions empty
        response = await client2.get("/events/my-subscriptions")
        assert response.json() == []


