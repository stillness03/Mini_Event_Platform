import jwt
import logging
from fastapi import Request, HTTPException

from app.core.config import Settings, get_settings

logger = logging.getLogger("gateway")

def verify_token(request: Request, settings: Settings | None = None):
    if settings is None:
        settings = get_settings

    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    
    token = auth_header.split(" ", 1)[1]

    try:
        jwt.decode(
            token, 
            settings.JWT_SECRET,
            algorithms = ["HS256"],
        )
    except jwt.PyJWTError as exc:
        logger.warning(f"Invalid token from {request.client.host}: {exc}")
        raise HTTPException(status_code=401, detail="Invalid token")