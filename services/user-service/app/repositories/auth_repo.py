import uuid
from app.models.users import User
from .base import BaseRepository

class AuthRepository(BaseRepository):
    def create_user(self, email: str, hashed_password: str, username: str) -> User:
        new_user = User(
            id=uuid.uuid4(),
            username=username,
            email=email,
            hashed_password=hashed_password,
            auth_role="user",
        )
        self.db.add(new_user)
        return new_user

    def get_user_by_id(self, user_id: str) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def delete_user(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()

    def update_user(self, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user