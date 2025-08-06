from sqlalchemy import ForeignKey, Table, Column, Integer

from .base import Base


organization_activity_rel_table = Table(
    "organization_activity_rel",
    Base.metadata,
    Column(
        "organization_id", Integer, ForeignKey("organizations.id"), primary_key=True
    ),
    Column("activity_id", Integer, ForeignKey("activities.id"), primary_key=True),
)
