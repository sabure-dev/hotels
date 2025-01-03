from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.security.password import get_password_hash
from .roles import get_role_by_title
from ..models.user import User
from ..models.role import Role
from api.v1.schemas import CreateUser, UserRole


async def create_user_crud(user: CreateUser, session: AsyncSession) -> User:
    existing_user = await get_user_by_email(session, user.email)
    role = await get_role_by_title(user.role, session)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user.password)

    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role_id=role.id,
        is_active=True,
        is_verified=False
    )
    session.add(db_user)
    await session.commit()
    return db_user


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(
        select(User).options(joinedload(User.role)).where(User.email == email)
    )
    return result.scalars().first()


async def get_user_by_id(user_id: int, session: AsyncSession) -> User | None:
    result = await session.execute(
        select(User).options(joinedload(User.role)).where(User.id == user_id)
    )
    return result.scalars().first()


async def update_user_fullname_crud(
        new_fullname: str,
        session: AsyncSession,
        current_user: User
) -> User:
    current_user.full_name = new_fullname
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return current_user


async def update_user_email_crud(
        new_email: str,
        session: AsyncSession,
        current_user: User
) -> User:
    existing_user = await get_user_by_email(session, new_email)
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    current_user.email = new_email
    current_user.is_verified = False
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return current_user


async def update_user_password_crud(
        user: User,
        new_password: str,
        session: AsyncSession
) -> User:
    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def delete_user_crud(current_user: User, session: AsyncSession):
    await session.delete(current_user)
    await session.commit()


async def list_users_crud(
        skip: int = 0,
        limit: int = 100,
        role: UserRole | None = None,
        active: bool | None = None,
        is_verified: bool | None = None,
        sort_by: str | None = None,
        order: str = "asc",
        session: AsyncSession = None
) -> list[User]:
    query = select(User).options(joinedload(User.role))

    if role:
        query = query.join(Role).where(Role.title == role)
    if active is not None:
        query = query.where(User.is_active == active)
    if is_verified is not None:
        query = query.where(User.is_verified == is_verified)

    if sort_by:
        order_column = getattr(User, sort_by)
        if order == "desc":
            order_column = order_column.desc()
        query = query.order_by(order_column)

    query = query.offset(skip).limit(limit)

    result = await session.execute(query)
    return result.scalars().all()
