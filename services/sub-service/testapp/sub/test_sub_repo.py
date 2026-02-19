import pytest

from app.repositories.sub_repository import SubRepository


@pytest.fixture()
def repo(db_session):
    return SubRepository(db_session)


def test_create_subscription(repo, db_session):
    sub = repo.create(event_id="event1", user_id="user1")
    db_session.commit()

    assert sub.id is not None
    assert sub.event_id == "event1"
    assert sub.user_id == "user1"


def test_get_by_event_and_user(repo, db_session):
    repo.create("event1", "user1")
    db_session.commit()

    sub = repo.get_by_event_and_user("event1", "user1")

    assert sub is not None
    assert sub.event_id == "event1"
    assert sub.user_id == "user1"


def test_get_by_event_and_user_not_found(repo):
    sub = repo.get_by_event_and_user("not-exist", "user1")

    assert sub is None


def test_list_user_sub(repo, db_session):
    repo.create("event1", "user1")
    repo.create("event2", "user1")
    repo.create("event3", "user2")
    db_session.commit()

    result = repo.list_user_sub("user1", offset=0, limit=10)

    assert len(result) == 2


def test_count_by_user(repo, db_session):
    repo.create("event1", "user1")
    repo.create("event2", "user1")
    repo.create("event3", "user2")
    db_session.commit()

    count = repo.count_by_user("user1")

    assert count == 2


def test_delete_subscription(repo, db_session):
    sub = repo.create("event1", "user1")
    db_session.commit()

    repo.delete(sub)
    db_session.commit()

    result = repo.get_by_event_and_user("event1", "user1")

    assert result is None