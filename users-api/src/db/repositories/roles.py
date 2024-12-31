from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas import RoleSchema
from db.models import Role


async def get_role_by_title(title: str, session: AsyncSession) -> RoleSchema:
    query = select(Role).where(Role.title == title)
    role = await session.execute(query)
    return role.scalar_one_or_none()
