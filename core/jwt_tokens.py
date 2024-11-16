from datetime import datetime, timedelta, UTC

from jose import jwt

from core.config import settings

ALGORITHM = "HS256"


def create_access_token(user_id: int, device_id: str = None) -> str:
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode = {"exp": expire, "sub": str(user_id)}
    if device_id:
        to_encode["dev"] = device_id
    encoded_jwt = jwt.encode(
        to_encode, settings.access_token_secret_key, algorithm=ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(user_id: int, device_id: str = None) -> str:
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.refresh_token_expire_minutes
    )
    to_encode = {"exp": expire, "sub": str(user_id)}
    if device_id:
        to_encode["dev"] = device_id
    encoded_jwt = jwt.encode(
        to_encode, settings.refresh_token_secret_key, algorithm=ALGORITHM
    )
    return encoded_jwt
