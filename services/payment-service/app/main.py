from contextlib import asynccontextmanager
from fastapi import FastAPI


from app.client.base import create_http_client
from app.core.logging import setup_logging
from app.routers.payments import router as payment_router
from app.webhooks import stripe as stripe_webhook

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.http_client = create_http_client()
    yield

    # Shutdown
    await app.state.http_client.aclose()

app = FastAPI(title="Payment Service",
              lifespan=lifespan
              )

app.include_router(payment_router)
app.include_router(stripe_webhook.router)


# ---- Health Checks ----
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ready")
async def ready():
    return {"status": "ready"}



