
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import verify_token

from app.models.users import User
from app.schemas.users import UserResponse


routers = APIRouter(prefix='/users', tags=['users'])

bearer_scheme = HTTPBearer()


def get_user_from_token(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = verify_token(creds.credentials)
    user_id = int(payload.get("sub"))
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
                     db: Session = Depends(get_db)):
    payload = verify_token(creds.credentials)
    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user



@routers.get("/me", response_model=UserResponse)
def get_current_user_endpoint(current_user: User = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)

@routers.get("/get-current-user", response_model=UserResponse)
def get_current_user_endpoint(current_user: User = Depends(get_user_from_token)):
    return UserResponse.from_orm(current_user)

def get_user_role(current_user: User = Depends(get_user_from_token)) -> str:
    return current_user.auth_role

@routers.get("/test-user", response_model=UserResponse)
def test_user():
    return UserResponse(
        id=1,
        username="testuser",
        email="test@gmail.com",
        auth_role="user",
        created_at=datetime.utcnow()
    )
