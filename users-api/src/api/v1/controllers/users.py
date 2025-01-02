from typing import Annotated
from fastapi import Depends, Body, Query, Response, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from db.session.database import get_session
from ..schemas import UserSchema, UserOut, CreateUser, UserRole, PasswordResetRequest
from ..services.users import UsersService


class UsersController:
    @staticmethod
    async def health():
        return {"status": "ok"}

    @staticmethod
    async def db_health_check(
        session: AsyncSession = Depends(get_session)
    ):
        return await UsersService.check_db_health(session)

    @staticmethod
    async def get_current_user_profile(
        email: str,
        session: AsyncSession = Depends(get_session)
    ) -> UserOut:
        """
        Получить информацию о текущем пользователе.
        Email получаем из заголовка X-User-Email, который устанавливает gateway
        """
        return await UsersService.get_user_by_email(email, session)

    @staticmethod
    async def list_users(
        skip: int = 0,
        limit: int = 100,
        role: UserRole | None = None,
        active: bool | None = None,
        is_verified: bool | None = None,
        sort_by: str = Query(None, enum=["created_at", "email", "full_name"]),
        order: str = Query("asc", enum=["asc", "desc"]),
        session: AsyncSession = Depends(get_session)
    ) -> list[UserOut]:
        """Получить список пользователей"""
        return await UsersService.list_users(
            skip=skip, limit=limit, role=role,
            active=active, is_verified=is_verified,
            sort_by=sort_by, order=order, session=session
        )

    @staticmethod
    async def get_user(
        user_id: int,
        session: AsyncSession = Depends(get_session)
    ) -> UserOut:
        return await UsersService.get_user_by_id(user_id, session)

    @staticmethod
    async def create_user(
        user: CreateUser,
        session: AsyncSession = Depends(get_session)
    ) -> UserOut:
        return await UsersService.create_user(user, session)

    @staticmethod
    async def update_user_fullname(
        email: str,
        new_fullname: Annotated[str, Body()],
        session: AsyncSession = Depends(get_session)
    ) -> UserOut:
        user = await UsersService.get_user_by_email(email, session)
        return await UsersService.update_user_fullname(new_fullname, session, user)

    @staticmethod
    async def update_user_email(
        email: str,
        new_email: Annotated[EmailStr, Body()],
        session: AsyncSession = Depends(get_session)
    ) -> UserOut:
        user = await UsersService.get_user_by_email(email, session)
        return await UsersService.update_user_email(new_email, session, user)

    @staticmethod
    async def delete_user(
        email: str,
        session: AsyncSession = Depends(get_session)
    ):
        user = await UsersService.get_user_by_email(email, session)
        await UsersService.delete_user(user, session)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @staticmethod
    async def request_password_reset(
        session: Annotated[AsyncSession, Depends(get_session)],
        email: Annotated[str, Body()]
    ):
        await UsersService.request_password_reset(session, email)
        return {"detail": "Password reset instructions sent to email"}

    @staticmethod
    async def reset_password(
        session: Annotated[AsyncSession, Depends(get_session)],
        password_reset_request: Annotated[PasswordResetRequest, Body()]
    ):
        await UsersService.reset_password(session, password_reset_request)
        return {"detail": "Successful password reset"}

    @staticmethod
    async def verify_email(
        token: str,
        session: AsyncSession = Depends(get_session)
    ):
        return await UsersService.verify_email(token, session)
