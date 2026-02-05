
# ====== created users test file ======
from app.models.users import User
from datetime import datetime

def test_create_user(db):
    user = User(
        username="testuser",
        email="test@gmail.com",
        hashed_password="hashed",
        auth_role="user",
        created_at=datetime.utcnow()
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    assert user.id is not None
    assert user.username == "testuser"
