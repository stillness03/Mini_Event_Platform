import pytest
from unittest.mock import AsyncMock, MagicMock

from fastapi import HTTPException

from app.service.sub_service import SubscriptionService
from app.clients.event_client import EventServiceUnavailable


@pytest.fixture()
def mock_repo():
    repo = MagicMock()
    return repo


@pytest.fixture()
def mock_event_client():
    client = MagicMock()
    client.get_event = AsyncMock()
    return client


@pytest.fixture()
def service(mock_repo, mock_event_client):
    return SubscriptionService(mock_repo, mock_event_client)

@pytest.mark.asyncio
async def test_subscribe_success(service, mock_repo, mock_event_client):
    mock_event_client.get_event.return_value = {
        "id": "event1",
        "owner_id": "owner123"
    }

    mock_repo.get_by_event_and_user.return_value = None
    mock_repo.create.return_value = MagicMock()

    result = await service.subscribe("event1", "user1")

    assert result["message"] == "Subscribed successfully"
    mock_repo.create.assert_called_once()
    mock_repo.commit.assert_called_once()


@pytest.mark.asyncio
async def test_subscribe_duplicate(service, mock_repo, mock_event_client):
    mock_event_client.get_event.return_value = {
        "id": "event1",
        "owner_id": "owner123"
    }

    mock_repo.get_by_event_and_user.return_value = MagicMock()

    result = await service.subscribe("event1", "user1")

    assert result["message"] == "Already subscribed"


@pytest.mark.asyncio
async def test_subscribe_own_event(service, mock_event_client):
    mock_event_client.get_event.return_value = {
        "id": "event1",
        "owner_id": "user1"
    }

    with pytest.raises(HTTPException) as exc:
        await service.subscribe("event1", "user1")

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_subscribe_event_not_found(service, mock_event_client):
    mock_event_client.get_event.return_value = None

    with pytest.raises(HTTPException) as exc:
        await service.subscribe("event1", "user1")

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_subscribe_event_service_unavailable(service, mock_event_client):
    mock_event_client.get_event.side_effect = EventServiceUnavailable()

    with pytest.raises(HTTPException) as exc:
        await service.subscribe("event1", "user1")

    assert exc.value.status_code == 503


@pytest.mark.asyncio
async def test_unsubscribe_success(service, mock_repo):
    mock_repo.get_by_event_and_user.return_value = MagicMock()

    result = await service.unsubscribe("event1", "user1")

    assert result["message"] == "Unsubscribed successfully"
    mock_repo.delete.assert_called_once()
    mock_repo.commit.assert_called_once()


@pytest.mark.asyncio
async def test_unsubscribe_not_found(service, mock_repo):
    mock_repo.get_by_event_and_user.return_value = None

    with pytest.raises(HTTPException) as exc:
        await service.unsubscribe("event1", "user1")

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_list_user_subscriptions(service, mock_repo):
    mock_repo.list_user_sub.return_value = ["sub1", "sub2"]
    mock_repo.count_by_user.return_value = 2

    result = await service.list_user_subscriptions(
        user_id="user1",
        page=1,
        page_size=10
    )

    assert result["total"] == 2
    assert len(result["items"]) == 2