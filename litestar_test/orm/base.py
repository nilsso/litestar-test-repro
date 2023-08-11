from typing import Any

from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy.orm.attributes import get_attribute, set_attribute


# NOTE: Comment out MappedAsDataclass and init=False and things work fine
class Base(
    MappedAsDataclass,  # <--
    DeclarativeBase,
    init=False,  # <-- comment out if not using MappedAsDataclass
):
    __abstract__ = True

    def update(self, **kwargs: Any):
        """Partial update."""
        for k, v in kwargs.items():
            if isinstance(v, dict):
                f = get_attribute if hasattr(self, "_sa_instance_state") else getattr
                f(self, k).update(**v)
            else:
                f = set_attribute if hasattr(self, "_sa_instance_state") else setattr
                f(self, k, v)

    def to_dict(self, exclude: set[str] | None = None) -> dict[str, Any]:
        """Convert model to dictionary.

        Returns:
            dict[str, Any]: A dict representation of the model
        """
        exclude = (
            {"_sentinel"}.union(self._sa_instance_state.unloaded).union(exclude or [])  # type: ignore[attr-defined]
        )
        return {field.name: getattr(self, field.name) for field in self.__table__.columns if field.name not in exclude}
