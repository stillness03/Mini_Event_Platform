import httpx

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.routers.proxy import router as proxy_router
from app.core.logging_config import setup_logging
from app.middlewares.middleware import logging_middleware
from app.middlewares.auth_middleware import auth_middleware
from app.core.config import get_settings

setup_logging()

app = FastAPI(title="API Gateway")

app.state.client = httpx.AsyncClient(timeout=get_settings().REQUEST_TIMEOUT)

app.middleware("http")(logging_middleware)
app.middleware("http")(auth_middleware)

app.include_router(proxy_router)


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/ready")
async def ready():
    settings = get_settings()
    urls = [
        settings.USER_SERVICE_URL, 
        settings.EVENT_SERVICE_URL, 
        settings.SUB_SERVICE_URL,
    ]
    async with httpx.AsyncClient(timeout=2) as client:
        for url in urls:
            try:
                await client.get(f"{url}/health")
            except Exception:
                return JSONResponse({"status": "not ready"}, status_code=503)
        return {"status": "ready"}