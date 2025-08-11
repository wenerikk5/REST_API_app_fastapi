import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import db_helper
from app import crud, schemas


_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.get(
    "/",
    response_model=list[schemas.BuildingOrganizationsRead],
)
async def get_buildings(
    db: Annotated[AsyncSession, Depends(db_helper.get_session)],
):
    """
    Получение списка всех зданий с их организациями.
    """
    buildings = await crud.list_buildings(db)
    return buildings


@router.get(
    "/{building_id}/organizations",
    response_model=list[schemas.OrganizationReadFull],
)
async def get_organizations_in_building(
    building_id: int,
    db: Annotated[AsyncSession, Depends(db_helper.get_session)],
):
    """
    Получение списка организаций, находящихся в здании с заданным ID.
    """
    building = await crud.get_building(db, building_id)
    if building is None:
        raise HTTPException(status_code=404, detail="Building not found")

    organizations = await crud.get_organizations_in_building(db, building_id)
    return organizations
