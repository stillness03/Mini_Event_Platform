from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from uuid import uuid4

import pytest
import pytest_asyncio

from unittest.mock import AsyncMock
from app.cache.dep_cache import get_cache

import os
from dotenv import load_dotenv

from app.service.event_service import EventService
from app.core.dependencies import get_event_repo, get_current_user
from shared.schemas import UserContext
from app.repositories.event import EventRepository
from app.main import app

load_dotenv()


#fixtures for user contexts
@pytest.fixture
def user():
    return UserContext(
        owner_id=str(ObjectId()),
        role="user",
    )

@pytest.fixture
def admin():
    return UserContext(
        owner_id=str(ObjectId()),
        role="admin",
    )


@pytest_asyncio.fixture
async def mongo_client():
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    yield client
    client.close()


@pytest_asyncio.fixture
async def mongo_test_db(mongo_client):
    db = mongo_client["test_db"]
    yield db
    await db.drop_collection("events")


@pytest.fixture
def event_repo(mongo_test_db):
    return EventRepository(mongo_test_db)

@pytest.fixture
def event_service(event_repo):
    mock_cache = AsyncMock()
    mock_cache.get.return_value = None
    mock_cache.set.return_value = None
    mock_cache.delete.return_value = None
    mock_cache.delete_pattern.return_value = None
    return EventService(event_repo, mock_cache)

#async http client fixture
@pytest_asyncio.fixture
async def async_client(event_repo):
    counter = {}
    mock_cache = AsyncMock()

    async def fake_incr_with_ttl(key, ttl):
        counter[key] = counter.get(key, 0) + 1
        return counter[key]

    mock_cache.incr_with_ttl.side_effect = fake_incr_with_ttl
    mock_cache.get.return_value = None
    mock_cache.set.return_value = None
    mock_cache.delete.return_value = None
    mock_cache.delete_pattern.return_value = None

    user_id = str(uuid4())

    app.dependency_overrides[get_event_repo] = lambda: event_repo
    app.dependency_overrides[get_cache] = lambda: mock_cache
    app.dependency_overrides[get_current_user] = lambda: UserContext(
        user_id=user_id, role="user"
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
