import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import db_helper
from app import crud, schemas


_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get("/", response_model=list[schemas.ActivityReadFull])
async def get_activities(
    db: Annotated[AsyncSession, Depends(db_helper.get_session)],
):
    """
    Получение списка всех видов деятельности, включая вложения
    """
    activities = await crud.list_activities(db)
    return activities


@router.get(
    "/{activity_id}/organizations", response_model=list[schemas.OrganizationReadFull]
)
async def get_organizations_by_activity_id(
    activity_id: int,
    db: Annotated[AsyncSession, Depends(db_helper.get_session)],
):
    """
    Получение списка организаций, относящихся к указанному виду деятельности.
    Если вид деятельнсти верхнего уровня, то возврашает все организации,
    относящиеся к его подвидам.
    Максимальный уровень вложенности вида деятельности - 3.
    """
    try:
        organizations = await crud.get_organizations_by_activity_id(db, activity_id)
    except ValueError as e:
        _logger.error(f"Error getting organizations for activity {activity_id}: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    return organizations
