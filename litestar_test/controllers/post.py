from litestar import Controller as BaseController, patch
from litestar import get, post
from litestar.exceptions import NotFoundException
from sqlalchemy import sql
from sqlalchemy.orm import Session

from ..dto import PostDTOs
from ..orm import Post
from ..tag import Tag


def _post(session: Session, id: int) -> Post:
    if post := session.get(Post, id):
        return post
    raise NotFoundException


def _posts(session: Session) -> list[Post]:
    return list(session.scalars(sql.select(Post)))


class Controller(BaseController):
    path = "/post"
    tags = [Tag.POST]

    @get(
        summary="Fetch many",
        return_dto=PostDTOs.one,
    )
    async def fetch_many(self, *, session: Session) -> list[Post]:
        return _posts(session)

    @get(
        "{id:int}",
        summary="Fetch one",
        return_dto=PostDTOs.one,
    )
    async def fetch_one(self, id: int, *, session: Session) -> Post:
        return _post(session, id)

    @get(
        "{id:int}/full",
        summary="Fetch one (full)",
        return_dto=PostDTOs.full,
    )
    async def fetch_one_full(self, id: int, *, session: Session) -> Post:
        return _post(session, id)

    @post(
        "/create",
        summary="Create",
        dto=PostDTOs.partial,
        return_dto=PostDTOs.one,
    )
    async def create(self, *, data: Post, session: Session) -> Post:
        post = data
        session.add(post)
        session.commit()
        return post

    @patch(
        "/update",
        summary="Update",
        dto=PostDTOs.one,
        return_dto=PostDTOs.one,
    )
    async def update(self, id: int, *, data: Post, session: Session) -> Post:
        post = _post(session, id)
        # post.update(**data.to_dict())
        # session.commit()
        # print(post.to_dict())
        return post
