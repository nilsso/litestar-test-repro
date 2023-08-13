from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(
    MappedAsDataclass,
    DeclarativeBase,
    init=False,
    kw_only=True,
):
    pass
