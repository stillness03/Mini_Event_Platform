from fastapi import Header, HTTPException, status
from shared import UserContext
from uuid import UUID

def get_current_user(
        x_user_id: UUID | None = Header(None),
        x_user_role: str = Header("user"),
) -> UserContext:
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthenticated",
        )

    return UserContext(
        user_id=x_user_id,
        role=x_user_role,
    )

