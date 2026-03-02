import uuid
import logging
from datetime import datetime, timezone, timedelta

import bcrypt
import jwt
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"

# Password hashing
def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password is too long")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )

# JWT token handling
def _create_token(data: dict, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        **data,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),
        "iss": settings.APP_NAME,
        "aud": settings.APP_NAME,
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(sub: str) -> str:
    return _create_token(
        {"sub": sub, "type": "access"},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

def create_refresh_token(sub: str) -> str:
    return _create_token(
        {"sub": sub, "type": "refresh"},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

def verify_token(token: str, expected_type: str = "access") -> dict:
    try:
        claims = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require":  ["exp", "sub", "jti", "type", "iss", "aud"]},
            audience=settings.APP_NAME,
            issuer=settings.APP_NAME,
        )

        if claims.get("type") != expected_type:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid token type: expected {expected_type}",
            )
        
        return claims
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        logger.warning("Invalid token attempt: %s", type(e).__name__)
        raise HTTPException(status_code=401, detail="Invalid token")