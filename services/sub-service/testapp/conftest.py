import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_current_user
from app.clients.event_client import get_event_client
from shared import UserContext

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_db(db_session):
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()


@pytest.fixture()
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def user_id():
    return uuid.uuid4()

# AUTH OVERRIDE
@pytest.fixture()
def override_auth(user_id):
    async def _fake_user():
        return UserContext(user_id=user_id, role="user")

    app.dependency_overrides[get_current_user] = _fake_user
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def override_get_db(db_session):
    def _override():
        yield db_session

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.pop(get_db, None)


# MOCK EVENT CLIENT
class MockEventClient:
    async def get_event(self, event_id: str):
        return {
            "id": event_id,
            "owner_id": "owner-test-id"
        }

@pytest.fixture()
def override_event_client():
    def _override():
        return MockEventClient()

    app.dependency_overrides[get_event_client] = _override
    yield
    app.dependency_overrides.pop(get_event_client, None)



@pytest.fixture()
def client(
    override_get_db, 
    override_auth, 
    override_event_client
    ):
    with TestClient(app) as c:
        yield c