import time
from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.routers.users import routers as users_routers
from app.routers.auth import router as auth_routers


app = FastAPI()

app.include_router(users_routers, tags=["users"])
app.include_router(auth_routers, tags=["auth"])


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/check-db")
def check_db(db: Session = Depends(get_db)):
    return {"status": "db session works!"}
