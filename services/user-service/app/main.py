import time
from fastapi import FastAPI, Request

from app.routers.users import router as users_router
from app.routers.auth import router as auth_router

app = FastAPI(title="user-service")

app.include_router(users_router)
app.include_router(auth_router)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}