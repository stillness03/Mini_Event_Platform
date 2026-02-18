from contextlib import asynccontextmanager
from fastapi import FastAPI


from app.clients.base import create_http_client
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.routers.subscription import router as subscription_router


setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.http_client = create_http_client()
    yield

    # Shutdown
    await app.state.http_client.aclose()

app = FastAPI(title="Subscription Service", 
              lifespan=lifespan
              )

app.include_router(subscription_router)


# ---- Health Checks ----
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ready")
async def ready():
    return {"status": "ready"}