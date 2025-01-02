from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.services.auth_service import AuthService
from api.v1.controllers.auth_controller import AuthController
from core.utils.util_jwt import TokenService
from db.repositories.user_repository import UserRepository
from db.database import get_session


async def get_user_repository(
        session: AsyncSession = Depends(get_session)
) -> UserRepository:
    return UserRepository(session)


async def get_token_service() -> TokenService:
    return TokenService()


async def get_auth_service(
        user_repository: UserRepository = Depends(get_user_repository),
        token_service: TokenService = Depends(get_token_service)
) -> AuthService:
    return AuthService(user_repository, token_service)


async def get_auth_controller(
        auth_service: AuthService = Depends(get_auth_service)
) -> AuthController:
    return AuthController(auth_service)
