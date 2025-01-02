from core.interfaces.auth_service import IAuthService
from core.exceptions.auth_exceptions import (
    InvalidCredentialsException,
    TokenExpiredException,
    InactiveUserException,
    UnverifiedEmailException
)
from core.utils.util_jwt import TokenService
from db.repositories.user_repository import UserRepository
from core.dto.auth_dto import LoginRequest, TokenResponse
from core.utils.password import verify_password
from fastapi import HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession


class AuthService(IAuthService):
    def __init__(self, user_repository: UserRepository, token_service: TokenService):
        self.user_repository = user_repository
        self.token_service = token_service

    async def authenticate_user(self, credentials: LoginRequest) -> TokenResponse:
        user = await self.user_repository.get_by_email(credentials.email)

        if not user or not self._verify_password(credentials.password, user.hashed_password):
            raise InvalidCredentialsException()

        if not user.is_active:
            raise InactiveUserException()

        if not user.is_verified:
            raise UnverifiedEmailException()

        return self.token_service.create_tokens(user)

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        try:
            payload = self.token_service.verify_token(refresh_token)
            user = await self.user_repository.get_by_email(payload["sub"])

            if not user:
                raise InvalidCredentialsException()

            if not user.is_active:
                raise InactiveUserException()

            if not user.is_verified:
                raise UnverifiedEmailException()

            return self.token_service.create_tokens(user)

        except TokenExpiredException:
            raise
        except InvalidCredentialsException:
            raise
        except Exception as e:
            raise InvalidCredentialsException()

    async def validate_token(self, token: str) -> dict:
        try:
            payload = self.token_service.verify_token(token)
            return payload
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password)
