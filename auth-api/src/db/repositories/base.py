from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.interfaces.repository import IRepository
from sqlalchemy import select

from db.models import User


class BaseRepository(IRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int):
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User:
        query = select(self.model).options(joinedload(self.model.role)).where(self.model.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
