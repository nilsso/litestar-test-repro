from itertools import chain
from typing import Annotated, Generic, NamedTuple, TypeAlias, TypeVar, assert_never

from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.dto import DTOConfig
from sqlalchemy import inspect

from .orm import Post, User
from .orm.base import Base

ModelT = TypeVar("ModelT", bound=Base)


def _column_names(
    model: type[ModelT],
    *,
    i: set[str] | None = None,
    e: set[str] | None = None,
    exclude_underscore=True,
) -> set[str]:
    """Get all "regular" column/attribute names for a table model

    Note that `i` include names and `e` exclude names are not mutually exclussive, but that first `i` names are added to
    `names` the set of `model` "regular" column/attribute names, then secondly `e` names are removed.

    Arguments:
        - i: Additional attribute names to include.
        - e: Attribute names to exclude.
    """
    mapper = inspect(model)
    names = set(
        k
        for k in mapper.columns.keys()
        if not exclude_underscore or not k.startswith("_")
    )
    if i:
        names |= i
    if e:
        names -= e
    return names


def _subattributes(path: str, names: set[str]) -> set[str]:
    """Make DTO sub-attribute name strings for inclusion/exclusion.

    Example:

    ```python
    print(_subfields("user", {"id", "name"}))
    # {"user.id", "user.id"}

    print(_subfields("posts", {"id", "title"}, True))
    # {"posts.0.id", "posts.0.title"}
    ```
    """
    return {f"{path}.{field}" for field in names}


_DTOIncludeArg: TypeAlias = set[str] | tuple[str, set[str]]
"""A single attribute name, a tuple of path and sub-attribute names, or tuple of path, names and `as_list` boolean."""


def _map_dto_include_arg(arg: _DTOIncludeArg) -> set[str]:
    """Map DTO include argument to subattributes name strings."""
    match arg:
        case set():
            return arg
        case (name, include):
            return _subattributes(name, include)
        case _ as unreachable:
            assert_never(unreachable)


def _dto_include(*args: _DTOIncludeArg) -> set[str]:
    """Make DTO include attribute names."""
    return set(chain.from_iterable(map(_map_dto_include_arg, args)))


class DTOs(NamedTuple, Generic[ModelT]):
    """Encapsulation of various model data transfer objects."""

    one: type[SQLAlchemyDTO[ModelT]]
    partial: type[SQLAlchemyDTO[ModelT]]
    full: type[SQLAlchemyDTO[ModelT]]
    create: type[SQLAlchemyDTO[ModelT]]


def _make_dtos(
    model: type[ModelT],
    include_own: set[str],
    *include_others: _DTOIncludeArg,
    create_exclude: set[str] = {"id"},
    max_nested_depth=0,
) -> DTOs[ModelT]:
    """Make DTOs for model.

    Arguments:
        - model: Model to make DTO for.
        - include_own: Model's attributes to include by name.
        - *include_others: Names to include in "full" DTO.
        - create_exclude: Names to exclude from "create" DTO.
        - max_nested_depth: The maximum depth of nested items allowed for data transfer.
    """
    include_all = set(
        chain(include_own, chain.from_iterable(map(_dto_include, include_others)))
    )
    dto_one = SQLAlchemyDTO[Annotated[model, DTOConfig(include=include_own)]]
    dto_partial = SQLAlchemyDTO[
        Annotated[model, DTOConfig(include=include_own, partial=True)]
    ]
    dto_full = SQLAlchemyDTO[
        Annotated[
            model, DTOConfig(include=include_all, max_nested_depth=max_nested_depth)
        ]
    ]
    dto_create = SQLAlchemyDTO[
        Annotated[model, DTOConfig(include=include_own - create_exclude)]
    ]
    return DTOs(
        one=dto_one,
        partial=dto_partial,
        full=dto_full,
        create=dto_create,
    )


COLS_USER = _column_names(User)
COLS_POST = _column_names(Post)

UserDTOs = _make_dtos(
    User,
    COLS_USER,
    ("posts", COLS_POST),
    max_nested_depth=1,
)

PostDTOs = _make_dtos(
    Post,
    COLS_POST,
    ("user", COLS_USER),
    max_nested_depth=1,
)
