from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins.int_id_pk import IntIdPkMixin

if TYPE_CHECKING:
    from .organization import Organization


class Building(IntIdPkMixin, Base):
    address: Mapped[str]
    latitude: Mapped[float] = mapped_column(index=True)
    longitude: Mapped[float] = mapped_column(index=True)

    organizations: Mapped[list["Organization"]] = relationship(
        "Organization",
        back_populates="building",
    )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} id:{self.id} ({self.address!r})"
