from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.users import User
from app.repositories.auth_repo import AuthRepository
from app.repositories.refresh_token_repo import RefreshTokenRepository
from app.schemas.users import UserResponse, UserUpdate, SessionResponse
from app.service.auth_service import AuthService

router = APIRouter(tags=["users"])

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(
        auth_repo=AuthRepository(db),
        token_repo=RefreshTokenRepository(db),
    )

@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@router.patch("/me", response_model=UserResponse)
def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    updated = service.update_user(str(current_user.id), **data.model_dump(exclude_unset=True))
    return UserResponse.model_validate(updated)


@router.get("/me/sessions", response_model=list[SessionResponse])
def my_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    token_repo = RefreshTokenRepository(db)
    return token_repo.get_active_sessions(str(current_user.id))


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    _: User = Depends(require_admin),
    service: AuthService = Depends(get_auth_service),
):
    user = service.auth_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    _: User = Depends(require_admin),
    service: AuthService = Depends(get_auth_service),
):
    service.delete_user(user_id)