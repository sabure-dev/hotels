import jwt
from datetime import datetime, timedelta, timezone

from ..config.settings import settings


def create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.smtp.email_verification_secret_key,
        algorithm=settings.smtp.email_verification_algorithm,
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            settings.smtp.email_verification_secret_key,
            algorithms=[settings.smtp.email_verification_algorithm]
        )
        return payload
    except jwt.InvalidTokenError:
        return None


def create_email_verification_token(email: str) -> str:
    expiration = timedelta(minutes=settings.smtp.email_verification_expire_minutes)
    return create_token(
        {"sub": email},
        expiration
    )
