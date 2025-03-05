import datetime as dt

import sqlmodel


class _BaseCoverageDownloadRequest(sqlmodel.SQLModel):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    request_datetime: dt.datetime
    entity_name: str | None
    is_public_sector: bool
    download_reason: str
    climatological_variable: str
    aggregation_period: str
    measure_type: str
    year_period: str


class _BaseCoverageDownloadRequestCreate(sqlmodel.SQLModel):
    request_datetime: dt.datetime
    entity_name: str | None
    is_public_sector: bool
    download_reason: str
    climatological_variable: str
    aggregation_period: str
    measure_type: str
    year_period: str


class ForecastCoverageDownloadRequest(_BaseCoverageDownloadRequest, table=True):
    climatological_model: str
    scenario: str
    time_window: str | None


class ForecastCoverageDownloadRequestCreate(_BaseCoverageDownloadRequestCreate):
    climatological_model: str
    scenario: str
    time_window: str | None


class HistoricalCoverageDownloadRequest(_BaseCoverageDownloadRequest, table=True):
    decade: str | None
    reference_period: str | None


class HistoricalCoverageDownloadRequestCreate(_BaseCoverageDownloadRequestCreate):
    decade: str | None
    reference_period: str | None
