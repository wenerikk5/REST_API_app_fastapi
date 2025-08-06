from pydantic import BaseModel, ConfigDict


class BuildingBase(BaseModel):
    address: str
    latitude: float
    longitude: float


class BuildingCreate(BuildingBase): ...


class BuildingRead(BuildingBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
