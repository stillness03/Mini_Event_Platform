import bcrypt
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = 7

def hash_password(password: str) -> str:
    if len(password.encode('utf-8')) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password is too long"
        )

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(
        password.encode('utf-8'), salt).decode('utf-8')
    return hashed_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
