from __future__ import annotations

from typing import Annotated

from litestar import Controller, Litestar, get, patch, post
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyInitPlugin, SQLAlchemySyncConfig, SyncSessionConfig
from litestar.dto import DTOConfig
from litestar.exceptions import NotFoundException
from sqlalchemy import create_engine, sql
from sqlalchemy.orm import Session

from .base import Base
from .post import Post
from .user import User

PostDTO = SQLAlchemyDTO[Post]
PostDTO_Create = SQLAlchemyDTO[Annotated[Post, DTOConfig(include={"title", "user_id"})]]
PostDTO_Partial = SQLAlchemyDTO[Annotated[Post, DTOConfig(include={"title", "user_id"}, partial=True)]]

DB_URI = "sqlite+pysqlite:///test.sqlite"


def db_init():
    engine = create_engine(DB_URI)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        user = User(id=1, name="John Smith", posts=[])
        session.add(user)
        session.add(Post(id=1, user_id=1, title="Foo", user=user))
        session.commit()


class UserController(Controller):
    path = "/user"
    tags = ["User"]


def _post(session: Session, id: int):
    if post := session.get(Post, id):
        return post
    raise NotFoundException


class PostController(Controller):
    path = "/post"
    tags = ["Post"]

    @get(return_dto=PostDTO)
    async def fetch_many(self, *, session: Session) -> list[Post]:
        return list(session.scalars(sql.select(Post)))

    @post(
        "/create",
        dto=PostDTO_Create,
        return_dto=PostDTO,
        signature_namespace={
            "User": User,
        },
    )
    async def create(self, *, data: Post, session: Session) -> Post:
        post = data
        session.add(post)
        session.commit()
        return post

    @patch(
        "/update",
        dto=PostDTO_Partial,
        return_dto=PostDTO,
    )
    async def update(self, id: int, *, data: Post, session: Session) -> Post:
        post = _post(session, id)
        return post


db_config = SQLAlchemySyncConfig(
    connection_string=DB_URI,
    session_dependency_key="session",
    session_config=SyncSessionConfig(
        expire_on_commit=False,
    ),
)
app = Litestar(
    route_handlers=[UserController, PostController],
    plugins=[SQLAlchemyInitPlugin(db_config)],
    on_startup=[db_init],
    signature_namespace={
        "User": User,
    },
)
