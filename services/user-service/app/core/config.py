from datetime import UTC, datetime, timedelta, timezone
from fastapi import HTTPException
import os
import jwt
from dotenv import load_dotenv

from app.core.security import get_env_int

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = get_env_int(
    "ACCESS_TOKEN_EXPIRE_MINUTES", 30
)
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_token(data: dict, expires_delta: timedelta):
    expire = datetime.now(timezone.utc) + expires_delta

    payload = data.copy()
    payload["exp"] = int(expire.timestamp())

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def create_access_token(sub: str):
    return create_token({"sub": sub}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

def create_refresh_token(sub: str):
    return create_token({"sub": sub, "type": "refresh"}, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


def verify_token(token: str):
    print("\n====================")
    print("RAW TOKEN RECEIVED:", repr(token))
    print("====================")

    try:
        claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_ts = claims.get("exp")
        print("EXPIRATION:", datetime.fromtimestamp(exp_ts, tz=UTC))
        print("NOW:", datetime.now(UTC))
        return claims
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception as e:
        print("JWT ERROR:", repr(e))
        raise HTTPException(status_code=401, detail="Invalid token")


def decode_token(token: str):
    try:
        return verify_token(token)
    except HTTPException as e:
        return {"detail": e.detail}
