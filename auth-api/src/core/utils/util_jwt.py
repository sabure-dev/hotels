import logging
from datetime import datetime, timedelta
import jwt
from core.config import settings
from core.dto.auth_dto import TokenResponse
from db.models.user import User
from core.exceptions.auth_exceptions import TokenExpiredException, InvalidCredentialsException

logger = logging.getLogger(__name__)


class TokenService:
    def __init__(self):
        with open(settings.auth_jwt.private_key_path, 'r') as f:
            self.private_key = f.read()
        with open(settings.auth_jwt.public_key_path, 'r') as f:
            self.public_key = f.read()

    def create_tokens(self, user: User) -> TokenResponse:
        logger.info(f"Creating tokens for user: {user.email}, role: {user.role.title}")
        access_token = self._create_token(
            user,
            timedelta(minutes=settings.auth_jwt.access_token_expire_minutes)
        )
        refresh_token = self._create_token(
            user,
            timedelta(days=settings.auth_jwt.refresh_token_expire_days)
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    def verify_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token,
                self.public_key,
                algorithms=[settings.auth_jwt.algorithm]
            )
        except jwt.ExpiredSignatureError:
            raise TokenExpiredException()
        except jwt.InvalidTokenError:
            raise InvalidCredentialsException()

    def _create_token(self, user: User, expires_delta: timedelta) -> str:
        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "exp": expire,
            "sub": user.email,
            "role": user.role.title
        }
        return jwt.encode(
            to_encode,
            self.private_key,
            algorithm=settings.auth_jwt.algorithm
        )
