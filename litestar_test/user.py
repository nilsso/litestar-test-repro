from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .post import Post


class User(Base, kw_only=True):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    posts: Mapped[list[Post]] = relationship(back_populates="user", default_factory=list)
