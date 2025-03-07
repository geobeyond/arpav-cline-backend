import datetime as dt
from typing import (
    Annotated,
    Optional,
)
import pydantic


class TimeSeriesDownloadRequestRead(pydantic.BaseModel):
    request_datetime: dt.datetime
    entity_name: str | None
    is_public_sector: bool
    download_reason: str
    climatological_variable: str
    aggregation_period: str
    measure_type: str
    year_period: str
    data_category: str
    longitude: float
    latitude: float


class TimeSeriesDownloadRequestCreate(pydantic.BaseModel):
    entity_name: Annotated[Optional[str], pydantic.Field(max_length=500)] = None
    is_public_sector: bool
    download_reason: Annotated[str, pydantic.Field(max_length=500)]
    coords: str
