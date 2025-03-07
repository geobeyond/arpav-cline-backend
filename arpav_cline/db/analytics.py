from typing import (
    Optional,
    Sequence,
)

import sqlalchemy
import sqlmodel

from ..schemas.analytics import (
    ForecastCoverageDownloadRequest,
    ForecastCoverageDownloadRequestCreate,
    HistoricalCoverageDownloadRequest,
    HistoricalCoverageDownloadRequestCreate,
    TimeSeriesDownloadRequest,
    TimeSeriesDownloadRequestCreate,
)
from .base import (
    add_substring_filter,
    get_total_num_records,
)


def get_forecast_coverage_download_request(
    session: sqlmodel.Session,
    download_request_id: int,
) -> Optional[ForecastCoverageDownloadRequest]:
    return session.get(ForecastCoverageDownloadRequest, download_request_id)


def list_forecast_coverage_download_requests(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    climatological_variable_name_filter: Optional[str] = None,
) -> tuple[Sequence[ForecastCoverageDownloadRequest], Optional[int]]:
    """List existing forecast coverage download requests."""
    statement = sqlmodel.select(ForecastCoverageDownloadRequest).order_by(
        ForecastCoverageDownloadRequest.request_datetime  # noqa
    )
    if climatological_variable_name_filter is not None:
        statement = add_substring_filter(
            statement,
            climatological_variable_name_filter,
            ForecastCoverageDownloadRequest.climatological_variable,
        )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_forecast_coverage_download_requests(
    session: sqlmodel.Session,
    climatological_variable_name_filter: Optional[str] = None,
) -> Sequence[ForecastCoverageDownloadRequest]:
    _, num_total = list_forecast_coverage_download_requests(
        session,
        limit=1,
        include_total=True,
        climatological_variable_name_filter=climatological_variable_name_filter,
    )
    result, _ = list_forecast_coverage_download_requests(
        session,
        limit=num_total,
        include_total=False,
        climatological_variable_name_filter=climatological_variable_name_filter,
    )
    return result


def create_forecast_coverage_download_request(
    session: sqlmodel.Session,
    download_request_create: ForecastCoverageDownloadRequestCreate,
) -> ForecastCoverageDownloadRequest:
    """Create a new forecast coverage download request."""
    db_download_request = ForecastCoverageDownloadRequest(
        **download_request_create.model_dump(),
    )
    session.add(db_download_request)
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        session.refresh(db_download_request)
    return db_download_request


def delete_forecast_coverage_download_request(
    session: sqlmodel.Session, download_request_id: int
) -> None:
    db_item = get_forecast_coverage_download_request(session, download_request_id)
    if db_item is not None:
        session.delete(db_item)
        session.commit()
    else:
        raise RuntimeError("Forecast coverage download request not found")


def get_historical_coverage_download_request(
    session: sqlmodel.Session,
    download_request_id: int,
) -> Optional[HistoricalCoverageDownloadRequest]:
    return session.get(HistoricalCoverageDownloadRequest, download_request_id)


def list_historical_coverage_download_requests(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    climatological_variable_name_filter: Optional[str] = None,
) -> tuple[Sequence[HistoricalCoverageDownloadRequest], Optional[int]]:
    """List existing historical coverage download requests."""
    statement = sqlmodel.select(HistoricalCoverageDownloadRequest).order_by(
        HistoricalCoverageDownloadRequest.request_datetime  # noqa
    )
    if climatological_variable_name_filter is not None:
        statement = add_substring_filter(
            statement,
            climatological_variable_name_filter,
            HistoricalCoverageDownloadRequest.climatological_variable,
        )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_historical_coverage_download_requests(
    session: sqlmodel.Session,
    climatological_variable_name_filter: Optional[str] = None,
) -> Sequence[HistoricalCoverageDownloadRequest]:
    _, num_total = list_historical_coverage_download_requests(
        session,
        limit=1,
        include_total=True,
        climatological_variable_name_filter=climatological_variable_name_filter,
    )
    result, _ = list_historical_coverage_download_requests(
        session,
        limit=num_total,
        include_total=False,
        climatological_variable_name_filter=climatological_variable_name_filter,
    )
    return result


def create_historical_coverage_download_request(
    session: sqlmodel.Session,
    download_request_create: HistoricalCoverageDownloadRequestCreate,
) -> HistoricalCoverageDownloadRequest:
    """Create a new historical coverage download request."""
    db_download_request = HistoricalCoverageDownloadRequest(
        **download_request_create.model_dump(),
    )
    session.add(db_download_request)
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        session.refresh(db_download_request)
    return db_download_request


def delete_historical_coverage_download_request(
    session: sqlmodel.Session, download_request_id: int
) -> None:
    db_item = get_forecast_coverage_download_request(session, download_request_id)
    if db_item is not None:
        session.delete(db_item)
        session.commit()
    else:
        raise RuntimeError("Historical coverage download request not found")


def get_time_series_download_request(
    session: sqlmodel.Session,
    download_request_id: int,
) -> Optional[TimeSeriesDownloadRequest]:
    return session.get(TimeSeriesDownloadRequest, download_request_id)


def list_time_series_download_requests(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    climatological_variable_name_filter: Optional[str] = None,
) -> tuple[Sequence[TimeSeriesDownloadRequest], Optional[int]]:
    """List existing time series download requests."""
    statement = sqlmodel.select(TimeSeriesDownloadRequest).order_by(
        TimeSeriesDownloadRequest.request_datetime  # noqa
    )
    if climatological_variable_name_filter is not None:
        statement = add_substring_filter(
            statement,
            climatological_variable_name_filter,
            TimeSeriesDownloadRequest.climatological_variable,
        )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_time_series_download_requests(
    session: sqlmodel.Session,
    climatological_variable_name_filter: Optional[str] = None,
) -> Sequence[TimeSeriesDownloadRequest]:
    _, num_total = list_time_series_download_requests(
        session,
        limit=1,
        include_total=True,
        climatological_variable_name_filter=climatological_variable_name_filter,
    )
    result, _ = list_time_series_download_requests(
        session,
        limit=num_total,
        include_total=False,
        climatological_variable_name_filter=climatological_variable_name_filter,
    )
    return result


def create_time_series_download_request(
    session: sqlmodel.Session,
    download_request_create: TimeSeriesDownloadRequestCreate,
) -> TimeSeriesDownloadRequest:
    """Create a new time series download request."""
    db_download_request = TimeSeriesDownloadRequest(
        **download_request_create.model_dump(),
    )
    session.add(db_download_request)
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        session.refresh(db_download_request)
    return db_download_request


def delete_time_series_download_request(
    session: sqlmodel.Session, download_request_id: int
) -> None:
    db_item = get_time_series_download_request(session, download_request_id)
    if db_item is not None:
        session.delete(db_item)
        session.commit()
    else:
        raise RuntimeError("Time series download request not found")
