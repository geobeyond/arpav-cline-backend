from typing import Annotated

import httpx
import pydantic
import sqlmodel
from fastapi import Depends

from .. import config
from ..db import get_engine


def get_settings() -> config.ArpavPpcvSettings:
    return config.get_settings()


def get_db_engine(settings: config.ArpavPpcvSettings = Depends(get_settings)):
    """Dependency for FastAPI to create a database engine."""
    yield get_engine(settings)


def get_db_session(engine=Depends(get_db_engine)):  # noqa: B008
    """Dependency for FastAPI to get a fresh database session.

    Use this on FastAPI path operations that need access to the db.
    """
    with sqlmodel.Session(engine) as session:
        yield session


def get_http_client(
    settings: config.ArpavPpcvSettings = Depends(get_settings),
) -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=settings.http_client_timeout_seconds)


def get_sync_http_client(
    settings: config.ArpavPpcvSettings = Depends(get_settings),
) -> httpx.Client:
    return httpx.Client(timeout=settings.http_client_timeout_seconds)


class CommonListFilterParameters(pydantic.BaseModel):  # noqa: D101
    offset: Annotated[int, pydantic.Field(ge=0)] = 0
    limit: Annotated[int, pydantic.Field(ge=0, le=100)] = 20


class CoverageDownloadAnalyticsParameters(pydantic.BaseModel):
    entity_name: str | None = None
    is_public_sector: bool
    download_reason: str
