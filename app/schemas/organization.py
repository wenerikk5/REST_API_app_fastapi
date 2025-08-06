from pydantic import BaseModel, ConfigDict


class OrganizationBase(BaseModel):
    name: str
    phones: list[str] = []
    building_id: int


class OrganizationCreate(OrganizationBase):
    activity_ids: list[int]


class OrganizationRead(OrganizationBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
