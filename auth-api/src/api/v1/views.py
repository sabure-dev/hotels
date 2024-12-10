from datetime import datetime, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, Response

from core.config import settings
from core.utils import send_password_reset_email, reset_password_util, send_verification_email
from . import schemas as user_schemas
from core.helpers import create_refresh_token, create_access_token
from core.schemas import TokenInfo
from core.validation import validate_auth_user, get_current_active_auth_user_for_refresh, get_current_active_auth_user
from db.crud import create_user_crud, delete_user_crud, get_user_by_email
from db.database import get_session
from .schemas import UserSchema, PasswordResetRequest

router = APIRouter(
    prefix="/api/v1",
    tags=["Auth"],
)


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
async def create_user(user: user_schemas.CreateUser, session: AsyncSession = Depends(get_session)):
    user = await create_user_crud(user_in=user, session=session)
    await send_verification_email(user)
    return user


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


@router.get("/password-reset")
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
