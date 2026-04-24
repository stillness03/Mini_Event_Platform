import pytest_asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.models.payments import Base
from app.repositories.payments_rep import PaymentRepository
from app.service.pay_service import PaymentService


TEST_DATABASE_URL = "sqlite+aiosqlite://"


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
def mock_event_client() -> AsyncMock:
    mock = AsyncMock()
    mock.get_event = AsyncMock()
    return mock


@pytest.fixture
def mock_stripe_gateway() -> MagicMock:
    mock = MagicMock()
    mock.create_checkout_session = MagicMock()
    return mock

@pytest_asyncio.fixture
def payment_repo(db_session) -> PaymentRepository:
    return PaymentRepository(db_session)


@pytest_asyncio.fixture
def mock_deps(mock_event_client, mock_stripe_gateway, payment_repo) -> dict:
    return {
        "repo": payment_repo,
        "event_client": mock_event_client,
        "stripe_gateway": mock_stripe_gateway,
    }


@pytest_asyncio.fixture
def service(mock_deps) -> PaymentService:
    return PaymentService(
        repo=mock_deps["repo"],
        event_client=mock_deps["event_client"],
        stripe_gateway=mock_deps["stripe_gateway"],
    )