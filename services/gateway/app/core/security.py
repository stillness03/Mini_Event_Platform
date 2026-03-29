import jwt
import logging
from fastapi import Request, HTTPException

from app.core.config import Settings, get_settings

logger = logging.getLogger("gateway")


def verify_token(request: Request, settings: Settings | None = None):
    if settings is None:
        settings = get_settings()

    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = auth_header.split(" ", 1)[1]


    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"],
            audience=["gateway", "user-service", "events-service", "sub-service"],
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except jwt.InvalidAudienceError:
        logger.warning(f"Invalid audience from {request.client.host}")
        raise HTTPException(status_code=401, detail="Invalid audience")

    except jwt.PyJWTError as exc:
        logger.warning(f"Invalid token from {request.client.host}: {exc}")
        raise HTTPException(status_code=401, detail="Invalid token")