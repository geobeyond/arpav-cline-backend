import datetime as dt

import sqlmodel


class _BaseDownloadRequest(sqlmodel.SQLModel):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    request_datetime: dt.datetime
    entity_name: str | None
    is_public_sector: bool
    download_reason: str
    climatological_variable: str
    aggregation_period: str
    measure_type: str
    year_period: str


class _BaseDownloadRequestCreate(sqlmodel.SQLModel):
    request_datetime: dt.datetime
    entity_name: str | None
    is_public_sector: bool
    download_reason: str
    climatological_variable: str
    aggregation_period: str
    measure_type: str
    year_period: str


class ForecastCoverageDownloadRequest(_BaseDownloadRequest, table=True):
    climatological_model: str
    scenario: str
    time_window: str | None


class ForecastCoverageDownloadRequestCreate(_BaseDownloadRequestCreate):
    climatological_model: str
    scenario: str
    time_window: str | None


class HistoricalCoverageDownloadRequest(_BaseDownloadRequest, table=True):
    decade: str | None
    reference_period: str | None


class HistoricalCoverageDownloadRequestCreate(_BaseDownloadRequestCreate):
    decade: str | None
    reference_period: str | None


class TimeSeriesDownloadRequest(_BaseDownloadRequest, table=True):
    data_category: str
    longitude: float
    latitude: float


class TimeSeriesDownloadRequestCreate(_BaseDownloadRequestCreate):
    data_category: str
    longitude: float
    latitude: float
