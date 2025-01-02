from fastapi import HTTPException, Header, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.utils.util_jwt import TokenService
from db.database import get_session
from ..schemas import LoginData, TokenResponse


class AuthController:
    token_service = TokenService()

    @staticmethod
    async def login(
        login_data: LoginData,
        session: AsyncSession = Depends(get_session)
    ) -> TokenResponse:
        # ... существующий код логина ...

    @staticmethod
    async def validate_token(authorization: str = Header(None)):
        """
        Валидирует JWT токен и возвращает информацию о пользователе.
        Используется API Gateway для проверки доступа.
        """
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header"
            )
        
        token = authorization.split(" ")[1]
        try:
            # Проверяем токен и получаем payload
            payload = AuthController.token_service.verify_token(token)
            
            # Устанавливаем заголовки с информацией о пользователе
            response = Response()
            response.headers["X-User-Email"] = payload["sub"]
            response.headers["X-User-Role"] = payload["role"]
            
            return response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            ) 