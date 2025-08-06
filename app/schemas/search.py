from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from pydantic_core import PydanticCustomError


class OrganizationSearchRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {"min_lat": 55.0, "max_lat": 59.0, "min_lng": 37.6, "max_lng": 37.62},
                {"activity_name": "Еда"},
            ]
        },
    )

    name: str | None = Field(None, description="Название организации")
    activity_name: str | None = Field(None, description="Название деятельности")

    # search in certain radius
    lat: float | None = Field(None, ge=-90, le=90, description="Широта")
    lng: float | None = Field(None, ge=-180, le=180, description="Долгота")
    radius: float | None = Field(None, gt=0, description="Радиус поиска в км")

    # search in rectangle sector
    min_lat: float | None = Field(None, ge=-90, le=90, description="Минимальная широта")
    max_lat: float | None = Field(
        None, ge=-90, le=90, description="Максимальная широта"
    )
    min_lng: float | None = Field(
        None, ge=-180, le=180, description="Минимальная долгота"
    )
    max_lng: float | None = Field(
        None, ge=-180, le=180, description="Максимальная долгота"
    )

    @model_validator(mode="after")
    def validate_filters(self) -> "OrganizationSearchRequest":
        """
        Валидация совместимости различных фильтров.
        """
        name = self.name
        activity_name = self.activity_name
        radius_fields = (self.lat, self.lng, self.radius)
        rect_fields = (self.min_lat, self.max_lat, self.min_lng, self.max_lng)

        if name and any([activity_name, *radius_fields, *rect_fields]):
            raise PydanticCustomError(
                "name_filter_conflict",
                "Используйте поиск либо по имени организации, либо по имени деятельности, либо по координатам по раздельности",
            )

        if activity_name and any([*radius_fields, *rect_fields]):
            raise PydanticCustomError(
                "activity_name_filter_conflict",
                "Используйте поиск либо по имени деятельности, либо по координатам по раздельности",
            )

        # Проверка на одновременное использование радиуса и прямоугольника
        if any(radius_fields) and any(rect_fields):
            raise PydanticCustomError(
                "geo_filter_conflict",
                "Используйте либо радиус (lat+lng+radius), либо прямоугольник (min/max lat/lng), но не оба метода одновременно",
            )

        # Проверка полноты параметров для радиуса
        if any(radius_fields) and not all(radius_fields):
            missing = [
                name
                for name, val in zip(["lat", "lng", "radius"], radius_fields)
                if val is None
            ]
            raise PydanticCustomError(
                "missing_radius_fields",
                f"Для поиска по радиусу необходимо указать все параметры: lat, lng и radius. Отсутствуют: {', '.join(missing)}",
            )

        # Проверка полноты параметров для прямоугольника
        if any(rect_fields):
            if not all(rect_fields):
                missing = [
                    name
                    for name, val in zip(
                        ["min_lat", "max_lat", "min_lng", "max_lng"], rect_fields
                    )
                    if val is None
                ]
                raise PydanticCustomError(
                    "missing_rect_fields",
                    f"Для поиска по прямоугольнику необходимо указать все границы. Отсутствуют: {', '.join(missing)}",
                )

            if self.max_lat <= self.min_lat:
                raise PydanticCustomError(
                    "invalid_lat_range",
                    f"max_lat ({self.max_lat}) должен быть больше min_lat ({self.min_lat})",
                )

            if self.max_lng <= self.min_lng:
                raise PydanticCustomError(
                    "invalid_lng_range",
                    f"max_lng ({self.max_lng}) должен быть больше min_lng ({self.min_lng})",
                )

        return self

    @field_validator("max_lat")
    @classmethod
    def validate_lat_range(cls, v, info):
        if (
            v is not None
            and info.data.get("min_lat") is not None
            and v <= info.data["min_lat"]
        ):
            raise ValueError("max_lat должен быть больше min_lat")
        return v

    @field_validator("max_lng")
    @classmethod
    def validate_lng_range(cls, v, info):
        if (
            v is not None
            and info.data.get("min_lng") is not None
            and v <= info.data["min_lng"]
        ):
            raise ValueError("max_lng должен быть больше min_lng")
        return v

    @model_validator(mode="before")
    @classmethod
    def replace_empty_strings_with_none(cls, data: dict) -> dict:
        return {k: None if v == "" else v for k, v in data.items()}
