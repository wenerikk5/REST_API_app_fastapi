from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins.int_id_pk import IntIdPkMixin
from .organization_activity_rel import organization_activity_rel_table

if TYPE_CHECKING:
    from .organization import Organization


class Activity(IntIdPkMixin, Base):
    __tablename__ = "activities"

    name: Mapped[str] = mapped_column(index=True)
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("activities.id"), nullable=True
    )

    parent: Mapped["Activity | None"] = relationship(
        "Activity", back_populates="children", remote_side="Activity.id"
    )
    children: Mapped[list["Activity"]] = relationship(
        "Activity", back_populates="parent"
    )
    organizations: Mapped[list["Organization"]] = relationship(
        secondary=organization_activity_rel_table, back_populates="activities"
    )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} id:{self.id} ({self.name!r})"
