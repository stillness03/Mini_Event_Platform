import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from faker import Faker
from httpx import AsyncClient, ASGITransport

from database import Base, get_db
from main import app
from app.models.events import Event, Subscription
from app.models.users import User
from app.routers.users import get_user_from_token


fake = Faker()

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def clean_db(db):
    db.query(Subscription).delete()
    db.query(Event).delete()
    db.query(User).delete()
    db.commit()


# Fixtures for creating test users

@pytest.fixture()
def test_user(db):
    user = User(
        username=fake.user_name(),
        email=fake.email(),
        hashed_password="hashed_password",
        auth_role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()

@pytest.fixture()
def test_user_2(db):
    user = User(
        username=fake.user_name(),
        email=fake.email(),
        hashed_password="hashed_password",
        auth_role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()

@pytest_asyncio.fixture
async def auth_async_client(test_user):
    def override_get_user_from_token():
        return test_user

    app.dependency_overrides[get_user_from_token] = override_get_user_from_token

    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()



@pytest_asyncio.fixture
def make_auth_client(db):
    async def _make(user):

        def override_get_user_from_token():
            return user

        def override_get_db():
            yield db

        app.dependency_overrides[get_user_from_token] = override_get_user_from_token
        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            yield client

        app.dependency_overrides.clear()

    return _make


