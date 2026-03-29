from jose import jwt
from .schemas import UserContext


def verify_access_token(token: str, secret_key: str, algorithm: str) -> UserContext:
    payload = jwt.decode(
        token,
        secret_key,
        algorithms=[algorithm],
        audience="user-service",
    )
    user_id = payload.get("sub")

    if not user_id:
        raise ValueError("Token missing 'sub' field")

    role = payload.get("role", "user")
    return UserContext(user_id=user_id, role=role)