from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Header, HTTPException, status
from fastapi import Depends
from datetime import datetime, timedelta, timezone

from app.schemas.events import UserContext
from app.repositories.event import EventRepository
from app.core.database import get_db


def get_event_repo(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> EventRepository:
    return EventRepository(db)


def get_current_user(
    x_user_id: str | None = Header(None),
    x_user_role: str | None = Header("user"),
) -> UserContext:
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthenticated",
        )

    return UserContext(
        owner_id=x_user_id or "mock-user-id", # for tests
        role=x_user_role,
    )

async def event_creation_rate_limit(
    repo: EventRepository = Depends(get_event_repo),
    user: UserContext = Depends(get_current_user),
):
    one_minute_ago = datetime.now(timezone.utc) - timedelta(minutes=1)

    count = await repo.count_created_after(
        owner_id=user.owner_id,
        after=one_minute_ago,
    )

    if count >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Event creation limit exceeded (5 per minute)",
        )