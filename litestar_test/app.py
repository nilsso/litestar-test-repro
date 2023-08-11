from __future__ import annotations

from os import environ

from dotenv import load_dotenv
from litestar import Litestar
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyInitPlugin, SQLAlchemySyncConfig, SyncSessionConfig
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session

from .controllers.post import Controller as PostController
from .controllers.user import Controller as UserController
from .orm.base import Base
from .orm import Post, User

CONTROLLERS = [
    PostController,
    UserController,
]

ROUTES = [
    *CONTROLLERS,
]

load_dotenv(".env.safe")
load_dotenv()

env_db_init = (v := environ.get("DB_INIT")) and v.lower() in ("1", "true")
env_db_uri = environ["DB_URI"]
assert env_db_uri is not None
print(f"Using {env_db_uri=}")


def startup():
    engine = create_engine(env_db_uri)
    if env_db_init:
        print("... Initializing")
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    if env_db_init:
        with Session(engine) as session:
            session.add_all(
                [
                    User(id=1, name="User 1"),
                    User(id=2, name="User 2"),
                ]
            )
            session.add_all(
                [
                    Post(user_id=1, id=1, title="Foo"),
                    Post(user_id=2, id=2, title="Bar"),
                    Post(user_id=1, id=3, title="Baz"),
                ]
            )
            session.commit()


db_config = SQLAlchemySyncConfig(
    connection_string=env_db_uri,
    session_dependency_key="session",
    session_config=SyncSessionConfig(
        expire_on_commit=False,
    ),
)
app = Litestar(
    route_handlers=ROUTES,
    plugins=[SQLAlchemyInitPlugin(db_config)],
    on_startup=[startup],
)
