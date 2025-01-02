from db.repositories.base import BaseRepository
from db.models.user import User


class UserRepository(BaseRepository):
    model = User
