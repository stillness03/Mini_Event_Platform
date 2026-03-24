from fastapi import APIRouter, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password
from app.repositories.auth_repo import AuthRepository
from app.repositories.refresh_token_repo import RefreshTokenRepository
from app.schemas.users import LoginRequest, UserCreate, AuthResponse, UserResponse
from app.service.auth_service import AuthService
from app.core.limiter import limiter
from app.core.security import verify_token

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer()

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(
        auth_repo=AuthRepository(db),
        token_repo=RefreshTokenRepository(db),
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def register(
    data: UserCreate,
    request: Request,
    service: AuthService = Depends(get_auth_service),
):
    user, access_token, refresh_token = service.register_user(
        email=data.email,
        hashed_password=hash_password(data.password),
        username=data.username,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )

@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")
def login(
    data: LoginRequest,
    request: Request,
    service: AuthService = Depends(get_auth_service),
):
    user, access_token, refresh_token = service.login_user(
        email=data.email,
        password=data.password,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )

@router.post("/refresh", response_model=AuthResponse)
@limiter.limit("10/minute")
def refresh(
    request: Request,
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    service: AuthService = Depends(get_auth_service),
):
    user, access_token, refresh_token = service.refresh_tokens(
        refresh_token=creds.credentials,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    service: AuthService = Depends(get_auth_service),
):
    service.logout(refresh_token=creds.credentials)


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
def logout_all(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    service: AuthService = Depends(get_auth_service),
):
    claims = verify_token(creds.credentials, expected_type="refresh")
    service.logout_all(user_id=claims["sub"])


