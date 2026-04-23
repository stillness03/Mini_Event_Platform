from fastapi import Header, HTTPException, status
from uuid import UUID
from shared import UserContext

def get_current_user(
        x_user_id: UUID = Header(None),
        x_user_role: str = Header("user")
    ) -> UserContext:
    if not x_user_id:
       raise HTTPException(
           status_code=status.HTTP_401_UNAUTHORIZED,
           detail="Unable to retrieve x_user_id",
       )

    return UserContext(
        user_id=x_user_id,
        role=x_user_role,
    )