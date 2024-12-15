from datetime import datetime, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from pydantic import EmailStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, Response

from core.config import settings
from core.utils import send_password_reset_email, reset_password_util, send_verification_email
from . import schemas as user_schemas
from core.helpers import create_refresh_token, create_access_token
from core.schemas import TokenInfo
from core.validation import validate_auth_user, get_current_active_auth_user_for_refresh, \
    get_current_active_auth_user, validate_create_user_role, get_admin_user
from db.crud import create_user_crud, delete_user_crud, get_user_by_email, update_user_fullname_crud, \
    update_user_email_crud, get_user_by_id, list_users_crud
from db.database import get_session
from .schemas import UserSchema, PasswordResetRequest

router = APIRouter(
    prefix="/api/v1",
    tags=["Auth"],
)


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/health/db")
async def db_health_check(session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unhealthy: {str(e)}"
        )


@router.get("/me", response_model=user_schemas.UserOut)
async def get_current_user_profile(
        user: user_schemas.UserSchema = Depends(get_current_active_auth_user)
):
    return user


@router.get("/admin/users", response_model=list[user_schemas.UserOut], dependencies=[Depends(get_admin_user)])
async def list_users(
        skip: int = 0,
        limit: int = 100,
        role: user_schemas.UserRole | None = None,
        active: bool | None = None,
        is_verified: bool | None = None,
        sort_by: str = Query(None, enum=["created_at", "email", "full_name"]),
        order: str = Query("asc", enum=["asc", "desc"]),
        session: AsyncSession = Depends(get_session)
):
    return await list_users_crud(skip=skip, limit=limit, role=role, active=active, is_verified=is_verified,
                                 session=session, sort_by=sort_by, order=order)


@router.get("/admin/users/{user_id}", response_model=user_schemas.UserOut, dependencies=[Depends(get_admin_user)])
async def get_user(
        user_id: int,
        session: AsyncSession = Depends(get_session)
):
    return await get_user_by_id(user_id, session)


@router.post("/login")
async def auth_user(user: user_schemas.ValidateUser = Depends(validate_auth_user)):
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=TokenInfo,
    response_model_exclude_none=True,
)
def auth_refresh_jwt(
        user: user_schemas.ValidateUser = Depends(get_current_active_auth_user_for_refresh),
):
    access_token = create_access_token(user)
    return TokenInfo(
        access_token=access_token,
    )


@router.post("/create", response_model=user_schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: Annotated[user_schemas.CreateUser, Depends(validate_create_user_role)],
                      session: AsyncSession = Depends(get_session)):
    user = await create_user_crud(user_in=user, session=session)
    await send_verification_email(user)
    return user


@router.patch("/update_fullname", response_model=user_schemas.UserOut, status_code=status.HTTP_200_OK)
async def update_user_fullname(
        new_fullname: Annotated[str, Body()], session: AsyncSession = Depends(get_session),
        user: UserSchema = Depends(get_current_active_auth_user)):
    updated_user = await update_user_fullname_crud(new_fullname=new_fullname, session=session, current_user=user)
    return updated_user


@router.patch("/update_email", response_model=user_schemas.UserOut, status_code=status.HTTP_200_OK)
async def update_user_email(
        new_email: Annotated[EmailStr, Body()], session: AsyncSession = Depends(get_session),
        user: UserSchema = Depends(get_current_active_auth_user)
):
    updated_user = await update_user_email_crud(new_email=new_email, session=session, current_user=user)
    await send_verification_email(user)
    return updated_user


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: UserSchema = Depends(get_current_active_auth_user),
                      session: AsyncSession = Depends(get_session)):
    await delete_user_crud(current_user=user, session=session)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/password-forgot", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(
        session: Annotated[AsyncSession, Depends(get_session)],
        email: Annotated[str, Body()]
):
    user = await get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    await send_password_reset_email(user)
    return {"detail": "Password reset instructions sent to email"}


@router.post("/password-reset")
async def reset_password(
        session: Annotated[AsyncSession, Depends(get_session)],
        password_reset_request: Annotated[PasswordResetRequest, Body()]
):
    await reset_password_util(session=session, password_reset_request=password_reset_request)

    return {"detail": "Successful password reset"}


@router.get("/verify-email")
async def verify_email(
        token: str,
        session: AsyncSession = Depends(get_session)
):
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
