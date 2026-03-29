import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.security import verify_token

logger = logging.getLogger("gateway")

PUBLIC_PATH = {
    "/health", "/ready", "/docs", "/openapi.json", "/redoc",
    "/users/auth/register",
    "/users/auth/login",
    "/users/auth/refresh",
}

async def auth_middleware(request: Request, call_next):
    if request.url.path in PUBLIC_PATH:
        return await call_next(request)

    try:
        payload = verify_token(request)
        request.state.user = payload

    except HTTPException as e:
        logger.warning(
            f"Auth failed [{request.method} {request.url.path}] "
            f"from {request.client.host}: {e.detail}"
        )
        return JSONResponse(status_code=e.status_code, 
                            content={"detail" : e.detail})

    return await call_next(request)