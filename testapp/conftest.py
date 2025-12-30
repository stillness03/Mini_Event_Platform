import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app
from app.models.users import User

from faker import Faker

fake = Faker()

# Фикстура engine
@pytest.fixture(scope="session")
def engine():
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

# Фикстура сессии БД
@pytest.fixture(scope="function")
def db(engine):
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

# Переопределяем Depends get_db
@pytest.fixture(autouse=True)
def override_get_db(db):
    def _override():
        yield db
    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.clear()

# Фейковый пользователь
@pytest.fixture(scope="session")
def test_user(engine):
    TestingSessionLocal = sessionmaker(bind=engine)
    db_session = TestingSessionLocal()

    user = User(
        username=fake.user_name(),
        email=fake.email(),
        hashed_password="hashed_password",
        auth_role="user"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    yield user
    db_session.close()

# Переопределяем get_current_user
from app.routers.users import get_current_user

@pytest.fixture(autouse=True, scope="session")
def override_get_current_user(test_user):
    async def _override():
        return test_user  # возвращаем объект пользователя
    app.dependency_overrides[get_current_user] = _override
    yield
    app.dependency_overrides.clear()