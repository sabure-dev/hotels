import sqlalchemy
from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy import select, desc, asc
from fastapi import status
from sqlalchemy.exc import SQLAlchemyError

from api.v1 import schemas as user_schemas
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas import UserSchema, PasswordResetRequest
import core.utils as utils
from db import models as user_models
from core import utils as auth_utils

ALLOWED_SORT_FIELDS = {'created_at', 'email', 'full_name'}
DEFAULT_LIMIT = 100
MAX_LIMIT = 1000


async def create_user_crud(user_in: user_schemas.CreateUser, session: AsyncSession) -> user_schemas.UserOut:
    try:
        role = await get_role_by_title(user_in.role.value, session)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role {user_in.role.value} not found"
            )

        hashed_password = auth_utils.hash_password(user_in.hashed_password)
        new_user = user_models.User(email=user_in.email,
                                    full_name=user_in.full_name,
                                    hashed_password=hashed_password,
                                    role_id=role.id)

        session.add(new_user)
        await session.commit()

        user_model = user_schemas.UserOut.model_validate(new_user)
        return user_model

    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists.")


async def get_user_by_id(user_id: int, session: AsyncSession) -> user_schemas.UserOut:
    query = select(user_models.User).where(user_models.User.id == user_id)
    response = await session.execute(query)
    user = response.scalars().first()

    return user


async def get_user_by_email(email: str, session: AsyncSession) -> user_schemas.UserOut:
    query = select(user_models.User).where(user_models.User.email == email)
    response = await session.execute(query)
    user = response.scalars().first()

    return user


async def get_user_model_by_email(email: str, session: AsyncSession) -> user_models.User:
    query = select(user_models.User).where(user_models.User.email == email)
    response = await session.execute(query)
    user = response.scalars().first()

    return user


async def update_user_fullname_crud(new_fullname: str, session: AsyncSession,
                                    current_user: user_schemas.UserSchema) -> user_schemas.UserOut:
    user = await get_user_by_id(current_user.id, session)
    user.full_name = new_fullname
    await session.commit()
    return user


async def update_user_email_crud(new_email: EmailStr, session: AsyncSession,
                                 current_user: user_schemas.UserSchema) -> user_schemas.UserOut:
    if new_email == current_user.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New email should be different")

    user = await get_user_by_id(current_user.id, session)
    user.email = new_email
    user.is_verified = False
    await session.commit()
    return user


async def delete_user_crud(current_user: UserSchema, session: AsyncSession):
    user_to_delete = await get_user_by_id(current_user.id, session)
    await session.delete(user_to_delete)
    await session.commit()
    return


async def reset_password_crud(session: AsyncSession, email: str, password_reset_request: PasswordResetRequest):
    user = await get_user_model_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if utils.validate_password(password_reset_request.new_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the current password"
        )

    user.hashed_password = utils.hash_password(password_reset_request.new_password)
    session.add(user)
    await session.commit()


async def get_role_by_title(title: str, session: AsyncSession) -> user_models.Role:
    query = select(user_models.Role).where(user_models.Role.title == title)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def list_users_crud(
        session: AsyncSession,
        skip: int = 0,
        limit: int = DEFAULT_LIMIT,
        role: str | None = None,
        active: bool | None = None,
        is_verified: bool | None = None,
        sort_by: str | None = None,
        order: str = "asc",
) -> list[user_schemas.UserOut]:
    try:
        limit = min(limit, MAX_LIMIT)

        if sort_by and sort_by not in ALLOWED_SORT_FIELDS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort field. Allowed fields: {', '.join(ALLOWED_SORT_FIELDS)}"
            )

        query = select(user_models.User)

        filters = {
            user_models.Role.title: role,
            user_models.User.active: active,
            user_models.User.is_verified: is_verified
        }

        active_filters = {k: v for k, v in filters.items() if v is not None}

        if role is not None:
            query = query.join(user_models.Role)

        for column, value in active_filters.items():
            query = query.where(column == value)

        sort_column = getattr(user_models.User, sort_by) if sort_by else user_models.User.id
        sort_func = desc if order.lower() == "desc" else asc
        query = query.order_by(sort_func(sort_column))

        query = query.offset(skip).limit(limit)

        result = await session.execute(query)
        users = result.scalars().all()

        return users

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
