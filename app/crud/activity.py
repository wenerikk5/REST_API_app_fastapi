from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app import models


async def list_activities(
    session: AsyncSession,
) -> Sequence[models.Activity]:
    stmt = select(models.Activity).options(
        selectinload(models.Activity.children),
    )
    result = await session.execute(stmt)
    return result.scalars().all()
