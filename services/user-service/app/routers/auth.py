from fastapi import Depends, HTTPException, status, APIRouter, Body
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer


from app.core.database import get_db
from app.models.users import User
from app.schemas.users import LoginRequest, UserCreate, AuthResponse, UserResponse
from app.core.config import create_access_token, create_refresh_token
from app.core.security import hash_password, verify_password


router = APIRouter(prefix='/auth', tags=['auth'])

bearer_scheme = HTTPBearer()

class UserValidator:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def validate_user_create(self, data: UserCreate):
        if self.db.query(User).filter(User.email == data.email).first():
            raise HTTPException(400, "Email already exists")

        if self.db.query(User).filter(User.username == data.username).first():
            raise HTTPException(400, "Username already exists")



@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register_user(data_user: UserCreate, db: Session = Depends(get_db), 
                  validator: UserValidator = Depends()):

    validator.validate_user_create(data_user)
   
    hashed_pwd = hash_password(data_user.password)
    new_user = User(
        username=data_user.username,
        email=data_user.email,
        hashed_password=hashed_pwd,
        auth_role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(sub=str(new_user.id))
    refresh_token = create_refresh_token(sub=str(new_user.id))

    return AuthResponse(
        user=UserResponse.model_validate(new_user),
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/login", response_model=AuthResponse)
def login_user(
    data: LoginRequest = Body(...), 
    db: Session = Depends(get_db)
):
    
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(sub=str(user.id))
    refresh_token = create_refresh_token(sub=str(user.id))

    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token
    )


