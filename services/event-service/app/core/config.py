from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
    # Mongo
    MONGO_URI: str
    DB_NAME: str

    # Business rules
    MAX_EVENTS_PER_HOUR: int = 5


settings = Settings(
    MONGO_URI=os.environ["MONGO_URI"],
    DB_NAME=os.environ["DB_NAME"],
    MAX_EVENTS_PER_HOUR=int(
        os.getenv("MAX_EVENTS_PER_HOUR", 5)
    ),
)
