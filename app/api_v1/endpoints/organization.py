import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import db_helper
from app import crud, schemas


_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("/", response_model=list[schemas.OrganizationReadFull])
async def get_organizations(
    db: Annotated[AsyncSession, Depends(db_helper.get_session)],
):
    """
    Получение списка всех организаций с их зданиями и видами деятельности.
    """
    organizations = await crud.get_organizations(db)
    return organizations


@router.get("/{organization_id}", response_model=schemas.OrganizationReadFull)
async def get_organization(
    organization_id: int,
    db: Annotated[AsyncSession, Depends(db_helper.get_session)],
):
    """
    Получение информации об организации по ID.
    """
    organization = await crud.get_organization(db, organization_id)
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization


@router.post("/search", response_model=list[schemas.OrganizationReadFull])
async def search_organizations(
    search_params: schemas.OrganizationSearchRequest,
    db: Annotated[AsyncSession, Depends(db_helper.get_session)],
):
    """
    Поиск организаций с возможностью фильтрации:
    - По названию организации
    - По названию вида деятельности
    - По радиусу от точки (lat, lng + radius)
    - По прямоугольной области (min_lat, max_lat, min_lng, max_lng)
    """
    try:
        return await crud.search_organizations(db, search_params)
    except ValueError as e:
        _logger.error(f"Error searching organizations: {e}")
        raise HTTPException(status_code=400, detail=str(e))
