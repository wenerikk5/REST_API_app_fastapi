from pydantic import ConfigDict

from .organization import OrganizationRead, OrganizationBase
from .building import BuildingBase, BuildingRead
from .activity import ActivityRead


class BuildingOrganizationsRead(BuildingBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    organizations: list["OrganizationRead"] = []


class OrganizationBuildingRead(OrganizationBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    building: "BuildingRead"


class OrganizationReadFull(OrganizationBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    building: "BuildingRead"
    activities: list["ActivityRead"]
