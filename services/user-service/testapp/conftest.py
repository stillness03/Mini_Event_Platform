import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from faker import Faker
from httpx import AsyncClient, ASGITransport
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.core.database import Base, get_db
from app.main import app
from app.models.users import User
from app.routers.users import get_user

settings = get_settings()

fake = Faker()

TEST_DATABASE_URL = settings.DATABASE_URL


engine = create_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
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

    with TestClient(app, headers={"User-Agent": "pytest-client"}) as c:
        yield c

    app.dependency_overrides.clear()

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
    def override_get_user():
        return test_user

    app.dependency_overrides[get_user] = override_get_user


    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()



@pytest_asyncio.fixture
def make_auth_client(db):
    async def _make(user):

        def override_get_user():
            return user

        def override_get_db():
            yield db

        app.dependency_overrides[get_user] = override_get_user
        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            yield client

        app.dependency_overrides.clear()

    return _make


