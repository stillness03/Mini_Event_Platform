from bson import ObjectId
from bson.errors import InvalidId


def to_object_id(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except InvalidId:
        raise ValueError("Invalid ObjectId")
