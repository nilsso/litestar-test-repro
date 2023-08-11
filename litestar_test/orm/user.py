from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .post import Post


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]

    posts: Mapped[list[Post]] = relationship(back_populates="user")