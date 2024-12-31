from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.session.base import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    users: Mapped[list["User"]] = relationship("User", back_populates="role")
