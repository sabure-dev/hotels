from core.interfaces.auth_service import IAuthService
from core.dto.auth_dto import LoginRequest, TokenResponse
from fastapi import Depends, Header, Response, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from db.database import get_session
from ..services.auth_service import AuthService


class AuthController:
    def __init__(self, auth_service: IAuthService):
        self.auth_service = auth_service

    async def login(self, credentials: LoginRequest) -> TokenResponse:
        return await self.auth_service.authenticate_user(credentials)

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        return await self.auth_service.refresh_token(refresh_token)

    async def validate_token(self, authorization: str) -> Response:
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header"
            )

        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization format. Must start with 'Bearer'"
            )

        token = authorization.split(" ")[1]
        payload = await self.auth_service.validate_token(token)

        response = Response()
        response.headers["X-User-Email"] = payload["sub"]
        response.headers["X-User-Role"] = payload["role"]

        return response
