from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .post import Post


class User(Base):
    __tablename__ = "user"

    name: Mapped[str]
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        default=None,  # <-- comment out if not using MappedAsDataclass
    )
    posts: Mapped[list[Post]] = relationship(
        back_populates="user",
        default_factory=list,  # <-- comment out if not using MappedAsDataclass
    )
