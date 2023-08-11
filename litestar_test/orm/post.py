from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .post_box import PostBox
    from .user import User


class Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]

    user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User | None] = relationship(back_populates="posts")

    box_id: Mapped[int] = mapped_column(ForeignKey("post_box.id"))
    box: Mapped[PostBox] = relationship(back_populates="posts")
