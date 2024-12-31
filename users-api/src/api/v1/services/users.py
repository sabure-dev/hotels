from datetime import datetime, timezone

import jwt
from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config.settings import settings
from core.monitoring.metrics import USER_REGISTRATIONS, PASSWORD_RESETS
from core.tasks.email import send_verification_email_task, send_password_reset_email_task
from db.repositories.users import (
    list_users_crud, get_user_by_id, create_user_crud,
    update_user_fullname_crud, update_user_email_crud,
    delete_user_crud, get_user_by_email, update_user_password_crud
)
from ..schemas import UserSchema, CreateUser, UserRole, PasswordResetRequest, UserOut


class UsersService:
    @staticmethod
    async def check_db_health(session: AsyncSession):
        try:
            await session.execute(text("SELECT 1"))
            return {"status": "healthy", "database": "connected"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database unhealthy: {str(e)}"
            )

    @staticmethod
    async def list_users(
            skip: int,
            limit: int,
            role: UserRole | None,
            active: bool | None,
            is_verified: bool | None,
            sort_by: str | None,
            order: str,
            session: AsyncSession
    ) -> list[UserOut]:
        return await list_users_crud(
            skip=skip, limit=limit, role=role,
            active=active, is_verified=is_verified,
            session=session, sort_by=sort_by, order=order
        )

    @staticmethod
    async def get_user_by_id(user_id: int, session: AsyncSession) -> UserOut:
        return await get_user_by_id(user_id, session)

    @staticmethod
    async def create_user(user: CreateUser, session: AsyncSession) -> UserOut:
        try:
            new_user = await create_user_crud(user, session)
            send_verification_email_task.delay(new_user.email)
            USER_REGISTRATIONS.labels(status="success").inc()
            return new_user
        except HTTPException as e:
            USER_REGISTRATIONS.labels(status="failure").inc()
            raise

    @staticmethod
    async def update_user_fullname(
            new_fullname: str,
            session: AsyncSession,
            current_user: UserSchema
    ) -> UserOut:
        return await update_user_fullname_crud(
            new_fullname=new_fullname,
            session=session,
            current_user=current_user
        )

    @staticmethod
    async def update_user_email(
            new_email: str,
            session: AsyncSession,
            current_user: UserSchema
    ) -> UserOut:
        updated_user = await update_user_email_crud(
            new_email=new_email,
            session=session,
            current_user=current_user
        )
        send_verification_email_task.delay(updated_user.email)
        return updated_user

    @staticmethod
    async def delete_user(current_user: UserSchema, session: AsyncSession):
        await delete_user_crud(current_user=current_user, session=session)

    @staticmethod
    async def request_password_reset(session: AsyncSession, email: str):
        try:
            user = await get_user_by_email(session=session, email=email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            send_password_reset_email_task.delay(user.email)
            PASSWORD_RESETS.labels(status="success").inc()
        except Exception as e:
            PASSWORD_RESETS.labels(status="failure").inc()
            raise

    @staticmethod
    async def reset_password(
            session: AsyncSession,
            password_reset_request: PasswordResetRequest
    ):
        try:
            payload = jwt.decode(
                password_reset_request.token,
                settings.smtp.email_verification_secret_key,
                algorithms=[settings.smtp.email_verification_algorithm]
            )

            if datetime.now(timezone.utc) > datetime.fromtimestamp(payload["exp"], tz=timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reset password link has expired"
                )

            email = payload["sub"]
            user = await get_user_by_email(session=session, email=email)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            await update_user_password_crud(
                user=user,
                new_password=password_reset_request.new_password,
                session=session
            )

            PASSWORD_RESETS.labels(status="success").inc()

        except jwt.InvalidTokenError:
            PASSWORD_RESETS.labels(status="failure").inc()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset password token"
            )
        except Exception as e:
            PASSWORD_RESETS.labels(status="failure").inc()
            raise

    @staticmethod
    async def verify_email(token: str, session: AsyncSession):
        try:
            payload = jwt.decode(
                token,
                settings.smtp.email_verification_secret_key,
                algorithms=[settings.smtp.email_verification_algorithm]
            )

            if datetime.now(timezone.utc) > datetime.fromtimestamp(payload["exp"], tz=timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Verification link has expired"
                )

            email = payload["sub"]
            user = await get_user_by_email(session=session, email=email)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            if user.is_verified:
                return {"message": "Email already verified"}

            user.is_verified = True
            session.add(user)
            await session.commit()

            return {"message": "Email verified successfully"}

        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
