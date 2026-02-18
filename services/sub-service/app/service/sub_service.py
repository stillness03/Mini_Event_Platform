import logging

from fastapi import HTTPException, status
from app.repositories.sub_repository import SubRepository
from app.clients.event_client import EventClient, EventServiceUnavailable


logger = logging.getLogger(__name__)


class SubscriptionService:
    def __init__(self, repo: SubRepository, event_client: EventClient):
        self.repo = repo
        self.event_client = event_client

    async def subscribe(self, event_id: str, user_id: str) -> dict:
        try:
            event = await self.event_client.get_event(event_id)
        except EventServiceUnavailable:
            logger.warning(
                "event_service_unavailable user_id=%s event_id=%s",
                    user_id,
                    event_id,
            )
            raise HTTPException(503, "Event service unavailable")
        
        if not event:
            raise HTTPException(
                status_code=404, 
                detail="Event not found"
                )

        if event["owner_id"] == user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot subscribe to your own event",
            )
        

        existing = self.repo.get_by_event_and_user(event_id, user_id)
        if existing:
            logger.info(
                "subscription_already_exists user_id=%s event_id=%s",
                user_id,
                event_id,
            )
            return {"message": "Already subscribed"}

        subscription = self.repo.create(event_id, user_id)
        self.repo.commit()
        self.repo.refresh(subscription)

        return {"message": "Subscribed successfully"}
    

    async def unsubscribe(self, event_id: str, user_id: str):
        subscription = self.repo.get_by_event_and_user(event_id, user_id)
        if not subscription:
            raise HTTPException(
                status_code=404, 
                detail="Subscription not found"
                )

        self.repo.delete(subscription)
        self.repo.commit()

        return {"message": "Unsubscribed successfully"}
    

    async def list_user_subscriptions(self, user_id: str, 
                                      page: int, page_size: int) -> dict:
        offset = (page - 1) * page_size
        subscriptions = self.repo.list_user_sub(user_id, offset, page_size)
        total = self.repo.count_by_user(user_id)
        return {
            "items": subscriptions,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
