from abc import ABC, abstractmethod
from core.dto.auth_dto import LoginRequest, TokenResponse


class IAuthService(ABC):
    @abstractmethod
    async def authenticate_user(self, credentials: LoginRequest) -> TokenResponse:
        pass

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        pass
