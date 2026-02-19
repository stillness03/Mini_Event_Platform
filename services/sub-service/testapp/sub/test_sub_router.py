
def test_subscribe_success(client):
    response = client.post("/events/subscribe/event-test-1")
    assert response.status_code == 201
    assert response.json()["message"] == "Subscribed successfully"

def test_subscribe_duplicate(client):
    client.post("/events/subscribe/event-test-dup")
    response = client.post("/events/subscribe/event-test-dup")
    assert response.status_code == 201
    assert response.json()["message"] == "Already subscribed"

def test_unsubscribe_success(client):
    client.post("/events/subscribe/event-test-unsub")
    response = client.post("/events/unsubscribe/event-test-unsub")
    assert response.status_code == 200
    assert response.json()["message"] == "Unsubscribed successfully"

def test_unsubscribe_not_found(client):
    response = client.post("/events/unsubscribe/not-exists-event")
    assert response.status_code == 404

def test_list_subscriptions_empty(client):
    response = client.get("/events/my-subscriptions")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []

def test_list_subscriptions_with_data(client):
    client.post("/events/subscribe/event-list-1")
    client.post("/events/subscribe/event-list-2")
    response = client.get("/events/my-subscriptions")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2

def test_list_subscriptions_pagination(client):
    for i in range(5):
        client.post(f"/events/subscribe/event-page-{i}")
    response = client.get("/events/my-subscriptions?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["items"]) == 2