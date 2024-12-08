import smtplib
import uuid
from datetime import datetime, timedelta, UTC, timezone
from email.mime.text import MIMEText

import bcrypt
import jwt
from fastapi import HTTPException
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.v1.schemas import PasswordResetRequest
from core.config import settings
from db.crud import get_user_model_by_email, reset_password_crud


def encode_jwt(
        payload: dict,
        private_key: str = settings.auth_jwt.private_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(UTC)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=int(expire_minutes))
    to_encode.update(
        exp=expire,
        iat=now,
        jti=str(uuid.uuid4()),
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
        token: str | bytes,
        public_key: str = settings.auth_jwt.public_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
) -> dict:
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )
    return decoded


def hash_password(
        password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(
        password: str,
        hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


async def send_password_reset_email(user):
    reset_token = create_password_reset_token(user)
    reset_url = f"http://localhost:8000/password-reset?token={reset_token}"

    msg = MIMEText(settings.smtp.reset_password_email_template.format(reset_url=reset_url))
    msg['Subject'] = 'Password Reset Instructions'
    msg['From'] = settings.smtp.smtp_user
    msg['To'] = user.email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(settings.smtp.smtp_user, settings.smtp.smtp_pass)
        smtp.send_message(msg)


def create_password_reset_token(user):
    data = {"sub": user.email,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.smtp.reset_password_token_expire_minutes)}
    return jwt.encode(data, settings.smtp.reset_password_secret_key, algorithm=settings.smtp.reset_password_algorithm)


async def reset_password_util(session: AsyncSession, password_reset_request: PasswordResetRequest):
    try:
        payload = jwt.decode(password_reset_request.token, settings.smtp.reset_password_secret_key,
                             algorithms=[settings.smtp.reset_password_algorithm])

        if datetime.now(timezone.utc) > datetime.fromtimestamp(payload["exp"], tz=timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token has expired"
            )

        email = payload["sub"]
        await reset_password_crud(email=email, session=session, password_reset_request=password_reset_request)
        return {"detail": "Password reset successful"}

    except (InvalidTokenError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )
