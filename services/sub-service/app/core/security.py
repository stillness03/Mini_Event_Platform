from fastapi import Header, HTTPException, status
from app.schemas.subcription import UserContext


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
        user_id=x_user_id or "mock-user-id",  # for tests
        role=x_user_role,
    )

