import time
from datetime import time as dt_time
from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
from database import get_db, engine, Base

from app.routers.users import routers as users_router
from app.routers.auth import router as auth_router
from app.routers.events import router as events_routers

app = FastAPI()

Base.metadata.create_all(bind=engine)


app.include_router(users_router, tags=["users"])
app.include_router(auth_router, tags=['auth'])
app.include_router(events_routers, tags=["events"])



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
