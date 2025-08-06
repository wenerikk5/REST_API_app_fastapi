from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY

from .base import Base
from .mixins.int_id_pk import IntIdPkMixin
from .organization_activity_rel import organization_activity_rel_table

if TYPE_CHECKING:
    from .building import Building
    from .activity import Activity


class Organization(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(index=True)
    phones: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True, default=[])
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"))

    building: Mapped["Building"] = relationship(back_populates="organizations")
    activities: Mapped[list["Activity"]] = relationship(
        secondary=organization_activity_rel_table,
        back_populates="organizations",
    )
