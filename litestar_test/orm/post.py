from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Post(Base):
    __tablename__ = "post"

    title: Mapped[str]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
    )
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        default=None,  # <-- comment out if not using MappedAsDataclass
    )
    user: Mapped[User] = relationship(
        back_populates="posts",
        default=None,  # <-- comment out if not using MappedAsDataclass
    )
