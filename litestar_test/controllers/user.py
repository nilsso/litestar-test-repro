from litestar import Controller as BaseController
from litestar import get, post
from sqlalchemy import sql
from litestar.exceptions import NotFoundException
from sqlalchemy.orm import Session

from ..dto import UserDTOs
from ..orm import User, Post
from ..tag import Tag


def _user(
    session: Session,
    id: int,
    *,
    full=False,
) -> User:
    q = sql.select(User).filter_by(id=id)
    if full:
        q = q.join(Post, isouter=True)
    if user := session.scalar(q):
        return user
    raise NotFoundException


def _users(session: Session) -> list[User]:
    return list(session.scalars(sql.select(User)))


class Controller(BaseController):
    path = "/user"
    tags = [Tag.USER]

    @get(
        summary="Fetch many",
        return_dto=UserDTOs.one,
    )
    async def fetch_many(self, *, session: Session) -> list[User]:
        return _users(session)

    @get(
        "{id:int}",
        summary="Fetch one",
        return_dto=UserDTOs.one,
    )
    async def fetch_one(self, id: int, *, session: Session) -> User:
        return _user(session, id)

    @get(
        "{id:int}/full",
        summary="Fetch one (full)",
        return_dto=UserDTOs.full,
    )
    async def fetch_one_full(self, id: int, *, session: Session) -> User:
        return _user(session, id, full=True)

    @post(
        "create",
        summary="Create one",
        dto=UserDTOs.create,
        return_dto=UserDTOs.one,
    )
    async def create_one(self, *, data: User, session: Session) -> User:
        session.add(data)
        session.commit()
        return data
