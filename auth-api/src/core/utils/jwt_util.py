from datetime import datetime, timedelta
from typing import Optional

import jwt
from core.config import settings


class TokenService:
    def __init__(self):
        self.private_key = settings.auth_jwt.private_key_path.read_text()
        self.public_key = settings.auth_jwt.public_key_path.read_text()
        self.algorithm = settings.auth_jwt.algorithm

    def create_tokens(self, user: "User") -> TokenInfo:
        access_token = self.create_access_token(user)
        refresh_token = self.create_refresh_token(user)
        return TokenInfo(
            access_token=access_token,
            refresh_token=refresh_token
        )

    def create_access_token(self, user: "User") -> str:
        return self._create_token(
            data={"sub": user.email, "type": "access"},
            expires_delta=timedelta(minutes=settings.auth_jwt.access_token_expire_minutes)
        )

    def create_refresh_token(self, user: "User") -> str:
        return self._create_token(
            data={"sub": user.email, "type": "refresh"},
            expires_delta=timedelta(days=settings.auth_jwt.refresh_token_expire_days)
        )

    def _create_token(self, data: dict, expires_delta: timedelta) -> str:
        payload = data.copy()
        expire = datetime.utcnow() + expires_delta
        payload.update({"exp": expire})

        return jwt.encode(
            payload,
            self.private_key,
            algorithm=self.algorithm
        )
