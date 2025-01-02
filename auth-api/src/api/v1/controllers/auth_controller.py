from core.interfaces.auth_service import IAuthService
from core.dto.auth_dto import LoginRequest, TokenResponse


class AuthController:
    def __init__(self, auth_service: IAuthService):
        self.auth_service = auth_service

    async def login(self, credentials: LoginRequest) -> TokenResponse:
        return await self.auth_service.authenticate_user(credentials)

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        return await self.auth_service.refresh_token(refresh_token)
