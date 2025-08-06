import json
import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app import models

_logger = logging.getLogger(__name__)


async def seed_test_data(session_factory: AsyncSession):
    async with session_factory() as db:
        try:
            # Check if data already exists
            result = await db.execute(select(models.Activity))
            if result.scalars().first() is not None:
                _logger.info("Test data already exists, skipping seed.")
                return

            _logger.info("Loading test data...")

            # Read JSON data
            data_path = Path(__file__).parent / "seed_data.json"
            with open(data_path, "r", encoding="utf-8") as f:
                test_data = json.load(f)

            # Add activities
            activity_records = {}

            for activity_data in test_data["activities"]:
                parent = activity_records.get(activity_data["parent_id"])
                activity = models.Activity(name=activity_data["name"], parent=parent)
                db.add(activity)
                await db.flush()
                activity_records[activity_data["id"]] = activity

            # Add buildings
            buildings = {}

            for building_data in test_data["buildings"]:
                building = models.Building(**building_data)
                db.add(building)
                await db.flush()
                buildings[building_data["id"]] = building.id

            # Add organizations
            for org_data in test_data["organizations"]:
                organization = models.Organization(
                    name=org_data["name"],
                    phones=org_data["phones"],
                    building_id=buildings[org_data["building_id"]],
                )
                activities = [activity_records[i] for i in org_data["activity_ids"]]
                organization.activities.extend(activities)
                db.add(organization)
                await db.flush()

            await db.commit()
            _logger.info(
                f"Successfully loaded: {len(test_data['activities'])} activities, "
                f"{len(test_data['buildings'])} buildings, "
                f"{len(test_data['organizations'])} organizations."
            )

        except IntegrityError as e:
            await db.rollback()
            _logger.error(f"Integrity error: {e}")
        except Exception as e:
            await db.rollback()
            _logger.error(f"Failed to load test data: {e}")
            raise
