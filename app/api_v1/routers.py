from fastapi import APIRouter

from app.api_v1.endpoints import (
    organizations_router,
    activity_router,
    building_router,
)


main_router = APIRouter()

main_router.include_router(organizations_router)
main_router.include_router(activity_router)
main_router.include_router(building_router)
