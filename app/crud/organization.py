import math
from typing import Sequence

from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from .utils import (
    get_child_activities,
    get_search_rectangle,
    calculate_distance,
)
from .building import get_buildings_in_rectangle


async def get_organization(
    session: AsyncSession,
    organization_id: int,
) -> models.Organization | None:
    stmt = (
        select(models.Organization)
        .options(
            joinedload(models.Organization.building),
            selectinload(models.Organization.activities),
        )
        .where(models.Organization.id == organization_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_organizations(
    session: AsyncSession,
) -> list[models.Organization]:
    stmt = select(models.Organization).options(
        joinedload(models.Organization.building),
        selectinload(models.Organization.activities),
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_organizations_by_activity_id(
    session: AsyncSession,
    activity_id: int,
) -> list[models.Organization]:
    activity_ids = await get_child_activities(session, activity_id=activity_id)

    stmt = (
        select(models.Organization)
        .join(models.Organization.activities)
        .where(models.Activity.id.in_(activity_ids))
        .options(
            joinedload(models.Organization.building),
            selectinload(models.Organization.activities),
        )
    )
    result = await session.execute(stmt)
    return result.scalars().unique().all()


async def get_organizations_by_activity_name(
    session: AsyncSession,
    activity_name: str,
) -> list[models.Organization]:
    activity_ids = await get_child_activities(session, activity_name=activity_name)

    stmt = (
        select(models.Organization)
        .join(models.Organization.activities)
        .where(models.Activity.id.in_(activity_ids))
        .options(
            joinedload(models.Organization.building),
            selectinload(models.Organization.activities),
        )
    )
    result = await session.execute(stmt)
    return result.scalars().unique().all()


async def get_organizations_in_rectangle(
    session: AsyncSession,
    lat_min: float,
    lat_max: float,
    lng_min: float,
    lng_max: float,
) -> list[models.Organization]:
    stmt = (
        select(models.Organization)
        .join(models.Organization.building)
        .where(
            and_(
                models.Building.latitude.between(lat_min, lat_max),
                models.Building.longitude.between(lng_min, lng_max),
            )
        )
        .options(
            joinedload(models.Organization.building),
            selectinload(models.Organization.activities),
        )
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def search_organizations(
    session: AsyncSession,
    search_params: schemas.OrganizationSearchRequest,
) -> list[models.Organization]:
    stmt = select(models.Organization).options(
        joinedload(models.Organization.building),
        selectinload(models.Organization.activities),
    )

    if search_params.name:
        stmt = (
            select(models.Organization)
            .where(models.Organization.name.ilike(f"%{search_params.name}%"))
            .options(
                joinedload(models.Organization.building),
                selectinload(models.Organization.activities),
            )
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    elif activity_name := search_params.activity_name:
        return await get_organizations_by_activity_name(
            session, activity_name=activity_name
        )

    elif all([search_params.lat, search_params.lng, search_params.radius]):
        lat = search_params.lat
        lng = search_params.lng
        radius = search_params.radius

        lat_min, lat_max, lng_min, lng_max = get_search_rectangle(lat, lng, radius)
        buildings_in_rectangle = await get_buildings_in_rectangle(
            session, lat_min, lat_max, lng_min, lng_max
        )

        building_ids = [
            b.id
            for b in buildings_in_rectangle
            if calculate_distance(lat, lng, b.latitude, b.longitude) <= radius
        ]
        stmt = (
            select(models.Organization)
            .where(models.Organization.building_id.in_(building_ids))
            .options(
                joinedload(models.Organization.building),
                selectinload(models.Organization.activities),
            )
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    elif any(
        [
            search_params.min_lat,
            search_params.max_lat,
            search_params.min_lng,
            search_params.max_lng,
        ]
    ):
        lat_min = search_params.min_lat
        lat_max = search_params.max_lat
        lng_min = search_params.min_lng
        lng_max = search_params.max_lng

        if not all([lat_min, lat_max, lng_min, lng_max]):
            raise ValueError("Для прямоугольного поиска нужно указать все 4 границы")

        return await get_organizations_in_rectangle(
            session,
            search_params.min_lat,
            search_params.max_lat,
            search_params.min_lng,
            search_params.max_lng,
        )

    raise ValueError("Не указаны параметры поиска")
