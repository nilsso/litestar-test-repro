from __future__ import annotations

from os import environ

from dotenv import load_dotenv
from litestar import Litestar
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyInitPlugin, SQLAlchemySyncConfig, SyncSessionConfig
from sqlalchemy.engine import create_engine

from .controllers.post import Controller as PostController
from .controllers.user import Controller as UserController
from .orm.base import Base

CONTROLLERS = [
    PostController,
    UserController,
]

ROUTES = [
    *CONTROLLERS,
]

load_dotenv(".env.safe")
load_dotenv()

DB_URI = environ["DB_URI"]
assert DB_URI is not None
print(f"Using {DB_URI=}")


def startup():
    engine = create_engine(DB_URI)
    Base.metadata.create_all(engine)


db_config = SQLAlchemySyncConfig(
    connection_string=DB_URI,
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
