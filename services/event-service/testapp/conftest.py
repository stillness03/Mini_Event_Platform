from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport

import pytest
import pytest_asyncio

import os
from dotenv import load_dotenv

from app.schemas.events import UserContext
from app.repositories.event import EventRepository
from app.main import app

load_dotenv()

TEST_DB_NAME = "test_db"


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


def override_user(user: UserContext):
    def _override():
        return user
    return _override


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


#async http client fixture
@pytest_asyncio.fixture
async def async_client(event_repo):
    from app.core.security import get_event_repo, get_current_user

    app.dependency_overrides[get_event_repo] = lambda: event_repo

    user_id = str(ObjectId())
    app.dependency_overrides[get_current_user] = lambda: UserContext(
        owner_id=user_id,
        role="user",
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()