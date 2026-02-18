from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from .base import BaseRepository


class SubRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)


    def create(self, event_id: str, user_id: str) -> Subscription: 
        subscription = Subscription(
            event_id=event_id,
            user_id=user_id,
        )
        self.db.add(subscription)
        return subscription


    def get_by_event_and_user(self, event_id: str, user_id: str) -> Subscription | None:
        return (
            self.db.query(Subscription)
            .filter(
                Subscription.event_id == event_id,
                Subscription.user_id == user_id
            )
            .first()
        )


    def list_user_sub(self, user_id: str, offset: int, limit: int
                      ) -> list[Subscription]:
        return (
        self.db.query(Subscription)
        .filter(Subscription.user_id == user_id)
        .order_by(Subscription.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


    def delete(self, subscription: Subscription):
        self.db.delete(subscription)


    def count_by_user(self, user_id: str) -> int:
        return (
            self.db.query(Subscription)
            .filter(Subscription.user_id == user_id)
            .count()
        )
