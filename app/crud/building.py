import math
from typing import Sequence

from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas


async def get_building(
    session: AsyncSession,
    building_id: int,
) -> models.Building | None:
    stmt = (
        select(models.Building)
        .options(
            selectinload(models.Building.organizations),
        )
        .where(models.Building.id == building_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_buildings(
    session: AsyncSession,
) -> list[models.Building]:
    stmt = select(models.Building).options(
        selectinload(models.Building.organizations),
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_organizations_in_building(
    session: AsyncSession,
    building_id: int,
) -> list[models.Organization]:
    stmt = (
        select(models.Organization)
        .where(models.Organization.building_id == building_id)
        .options(
            joinedload(models.Organization.building),
            selectinload(models.Organization.activities),
        )
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_buildings_in_rectangle(
    session: AsyncSession,
    lat_min: float,
    lat_max: float,
    lng_min: float,
    lng_max: float,
) -> list[models.Building]:
    stmt = (
        select(models.Building)
        .where(
            and_(
                models.Building.latitude.between(lat_min, lat_max),
                models.Building.longitude.between(lng_min, lng_max),
            )
        )
        .options(
            selectinload(models.Building.organizations),
        )
    )
    result = await session.execute(stmt)
    return result.scalars().all()
