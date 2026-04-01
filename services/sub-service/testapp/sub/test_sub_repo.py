import pytest
from faker import Faker
from app.repositories.sub_repository import SubRepository
import uuid

fake = Faker()

@pytest.fixture
def user_id():
    return uuid.uuid4()

@pytest.fixture
def other_user_id():
    return uuid.uuid4()

@pytest.fixture
def event_id():
    return str(uuid.uuid4())

@pytest.fixture()
def repo(db_session):
    return SubRepository(db_session)


def test_create_subscription(repo, db_session, event_id, user_id):
    sub = repo.create(event_id, user_id)
    db_session.commit()

    assert sub.id is not None
    assert sub.event_id == event_id
    assert sub.user_id == user_id


def test_get_by_event_and_user(repo, db_session, event_id, user_id):
    repo.create(event_id, user_id)
    db_session.commit()

    sub = repo.get_by_event_and_user(event_id, user_id)

    assert sub is not None
    assert sub.event_id == event_id
    assert sub.user_id == user_id


def test_get_by_event_and_user_not_found(repo, user_id):
    sub = repo.get_by_event_and_user("not-exist", user_id)

    assert sub is None


def test_list_user_sub(repo, db_session, event_id, user_id, other_user_id):
    repo.create(str(uuid.uuid4()), user_id)
    repo.create(str(uuid.uuid4()), user_id)
    repo.create(str(uuid.uuid4()), other_user_id)
    db_session.commit()

    result = repo.list_user_sub(user_id, offset=0, limit=10)

    assert len(result) == 2


def test_count_by_user(repo, db_session, event_id, user_id, other_user_id):
    repo.create(str(uuid.uuid4()), user_id)
    repo.create(str(uuid.uuid4()), user_id)
    repo.create(str(uuid.uuid4()), other_user_id)
    db_session.commit()

    count = repo.count_by_user(user_id)

    assert count == 2


def test_delete_subscription(repo, db_session, event_id, user_id):
    sub = repo.create(event_id, user_id)
    db_session.commit()

    repo.delete(sub)
    db_session.commit()

    result = repo.get_by_event_and_user(event_id, user_id)

    assert result is None