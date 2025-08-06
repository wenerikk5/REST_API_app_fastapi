import math
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app import models

_logger = logging.getLogger(__name__)


async def get_child_activities(
    session: AsyncSession,
    *,
    activity_id: int = None,
    activity_name: str = None,
) -> list[int]:
    if activity_id is None and activity_name is None:
        raise ValueError("Either activity_id or activity_name must be provided")

    stmt = select(models.Activity).options(selectinload(models.Activity.children))

    if activity_id is not None:
        stmt = stmt.where(models.Activity.id == activity_id)
    else:
        stmt = stmt.where(models.Activity.name.ilike(f"%{activity_name}%"))

    result = await session.execute(stmt)
    activity = result.scalar_one_or_none()

    if activity is None:
        _logger.warning(f"Activity not found: id={activity_id}, name={activity_name}")
        raise ValueError("Activity not found")

    children_ids = [child.id for child in activity.children]

    # deepest level of activity
    if len(children_ids) == 0:
        return [activity.id]

    # current activity in level 2, so children in level 3
    if activity.parent_id:
        return children_ids

    # current level is 1, grandchildren might exists
    return await get_grandchildren_activities(session, children_ids)


async def get_grandchildren_activities(
    session: AsyncSession,
    children_ids: list[int],
) -> list[int]:
    stmt = (
        select(models.Activity)
        .where(models.Activity.id.in_(children_ids))
        .options(selectinload(models.Activity.children))
    )

    result = await session.execute(stmt)
    activities = result.scalars().all()

    activity_ids = []
    for activity in activities:
        if len(activity.children) == 0:
            activity_ids.append(activity.id)
        else:
            activity_ids.extend([c.id for c in activity.children])

    return activity_ids


# Earth's radius in kilometers
EARTH_RADIUS_KM = 6371.0


def get_search_rectangle(
    lat: float, lng: float, radius_km: float
) -> tuple[float, float, float, float]:
    lat_rad = math.radians(lat)
    lng_rad = math.radians(lng)

    # Calculate the latitude and longitude bounds
    lat_min = lat_rad - (radius_km / EARTH_RADIUS_KM)
    lat_max = lat_rad + (radius_km / EARTH_RADIUS_KM)
    lng_min = lng_rad - (radius_km / (EARTH_RADIUS_KM * math.cos(lat_rad)))
    lng_max = lng_rad + (radius_km / (EARTH_RADIUS_KM * math.cos(lat_rad)))

    return (
        math.degrees(lat_min),
        math.degrees(lat_max),
        math.degrees(lng_min),
        math.degrees(lng_max),
    )


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lng2 - lng1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    return EARTH_RADIUS_KM * c
