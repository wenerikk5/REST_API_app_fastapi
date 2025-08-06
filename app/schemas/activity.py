from pydantic import BaseModel, ConfigDict


class ActivityBase(BaseModel):
    name: str
    parent_id: int | None


class ActivityCreate(ActivityBase): ...


class ActivityRead(ActivityBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int


class ActivityReadFull(ActivityBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    parent: "ActivityRead | None"
    children: list["ActivityRead"]
