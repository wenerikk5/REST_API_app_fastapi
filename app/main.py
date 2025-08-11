import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import ORJSONResponse

from app.core.config import settings
from app.api_v1.routers import main_router
from app.models.db_helper import db_helper
from app.common.dependencies import AuthorizationRequired

from .utils import seed_test_data

logging.basicConfig(
    level=settings.logging.log_level_value,
    format=settings.logging.log_format,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    logging.info("Starting application...")
    await seed_test_data(db_helper.session_factory)

    yield

    # shutdown
    await db_helper.dispose()


app = FastAPI(
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "filter": True,
        "tryItOutEnabled": True,
    },
)

app.include_router(
    main_router,
    prefix=settings.api_v1_str,
    dependencies=[Depends(AuthorizationRequired())],
)
