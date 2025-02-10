import json
import logging
import math
from typing import (
    Annotated,
    Optional,
)

import fastapi
import pandas as pd
import pydantic
from fastapi import (
    APIRouter,
    Depends,
    Header,
    Path,
    Request,
    Query,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from sqlmodel import Session

from .... import (
    database as db,
    operations,
)
from ....config import ArpavPpcvSettings
from ...responses import GeoJsonResponse
from ....schemas import base
from ... import dependencies
from ..schemas import observations
from ..schemas.geojson import observations as observations_geojson
from ..schemas.base import (
    TimeSeries,
    TimeSeriesItem,
    TimeSeriesList,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/stations",
    response_class=GeoJsonResponse,
    response_model=observations_geojson.StationFeatureCollection,
    responses={
        200: {
            "content": {"application/json": {}},
            "description": (
                "Return a GeoJSON feature collection or a custom JSON "
                "representation of the stations"
            ),
        }
    },
)
def list_stations(
    request: Request,
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    list_params: Annotated[dependencies.CommonListFilterParameters, Depends()],
    variable_name: str | None = None,
    temporal_aggregation: Annotated[
        base.ObservationAggregationType, Query()
    ] = base.ObservationAggregationType.SEASONAL,
    accept: Annotated[str | None, Header()] = None,
):
    """List known stations."""
    filter_kwargs = {}
    if variable_name is not None:
        if (db_var := db.get_variable_by_name(db_session, variable_name)) is not None:
            filter_kwargs.update(
                {
                    "variable_id_filter": db_var.id,
                    "variable_aggregation_type": temporal_aggregation,
                }
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid variable name")
    stations, filtered_total = db.list_stations(
        db_session,
        limit=list_params.limit,
        offset=list_params.offset,
        include_total=True,
        **filter_kwargs,
    )
    _, unfiltered_total = db.list_stations(
        db_session, limit=1, offset=0, include_total=True
    )
    if accept == "application/json":
        result = JSONResponse(
            content=jsonable_encoder(
                observations.StationList.from_items(
                    stations,
                    request,
                    limit=list_params.limit,
                    offset=list_params.offset,
                    filtered_total=filtered_total,
                    unfiltered_total=unfiltered_total,
                )
            )
        )
    else:
        result = observations_geojson.StationFeatureCollection.from_items(
            stations,
            request,
            limit=list_params.limit,
            offset=list_params.offset,
            filtered_total=filtered_total,
            unfiltered_total=unfiltered_total,
        )
    return result


@router.get(
    "/stations/{station_id}",
    response_model=observations.StationReadListItem,
)
def get_station(
    request: Request,
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    station_id: pydantic.UUID4,
):
    db_station = db.get_station(db_session, station_id)
    return observations.StationReadListItem.from_db_instance(db_station, request)


@router.get("/variables", response_model=observations.VariableList)
def list_variables(
    request: Request,
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    list_params: Annotated[dependencies.CommonListFilterParameters, Depends()],
):
    """List known variables."""
    variables, filtered_total = db.list_variables(
        db_session,
        limit=list_params.limit,
        offset=list_params.offset,
        include_total=True,
    )
    _, unfiltered_total = db.list_variables(
        db_session, limit=1, offset=0, include_total=True
    )
    return observations.VariableList.from_items(
        variables,
        request,
        settings,
        limit=list_params.limit,
        offset=list_params.offset,
        filtered_total=filtered_total,
        unfiltered_total=unfiltered_total,
    )


@router.get(
    "/variables/{variable_id}",
    response_model=observations.VariableReadListItem,
)
def get_variable(
    request: Request,
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    variable_id: pydantic.UUID4,
):
    db_variable = db.get_variable(db_session, variable_id)
    return observations.VariableReadListItem.from_db_instance(
        db_variable, request, settings
    )


@router.get("/monthly-measurements", response_model=observations.MonthlyMeasurementList)
def list_monthly_measurements(
    request: Request,
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    list_params: Annotated[dependencies.CommonListFilterParameters, Depends()],
    station_code: str | None = None,
    variable_name: str | None = None,
    month: Annotated[int | None, fastapi.Query(le=1, ge=12)] = None,
):
    """List known monthly measurements."""
    if station_code is not None:
        db_station = db.get_station_by_code(db_session, station_code)
        if db_station is not None:
            station_id = db_station.id
        else:
            raise ValueError("Invalid station code")
    else:
        station_id = None
    if variable_name is not None:
        db_variable = db.get_variable_by_name(db_session, variable_name)
        if db_variable is not None:
            variable_id = db_variable.id
        else:
            raise ValueError("Invalid variable name")
    else:
        variable_id = None
    monthly_measurements, filtered_total = db.list_monthly_measurements(
        db_session,
        limit=list_params.limit,
        offset=list_params.offset,
        station_id_filter=station_id,
        variable_id_filter=variable_id,
        month_filter=month,
        include_total=True,
    )
    _, unfiltered_total = db.list_monthly_measurements(
        db_session, limit=1, offset=0, include_total=True
    )
    return observations.MonthlyMeasurementList.from_items(
        monthly_measurements,
        request,
        limit=list_params.limit,
        offset=list_params.offset,
        filtered_total=filtered_total,
        unfiltered_total=unfiltered_total,
    )


@router.get(
    "/monthly-measurements/{monthly_measurement_id}",
    response_model=observations.MonthlyMeasurementReadListItem,
)
def get_monthly_measurement(
    request: Request,
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    monthly_measurement_id: pydantic.UUID4,
):
    db_monthly_measurement = db.get_monthly_measurement(
        db_session, monthly_measurement_id
    )
    return observations.MonthlyMeasurementReadListItem.from_db_instance(
        db_monthly_measurement, request
    )


@router.get(
    "/seasonal-measurements", response_model=observations.SeasonalMeasurementList
)
def list_seasonal_measurements(
    request: Request,
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    list_params: Annotated[dependencies.CommonListFilterParameters, Depends()],
    station_code: str | None = None,
    variable_name: str | None = None,
    season: base.Season | None = None,
):
    """List known seasonal measurements."""
    if station_code is not None:
        db_station = db.get_station_by_code(db_session, station_code)
        if db_station is not None:
            station_id = db_station.id
        else:
            raise ValueError("Invalid station code")
    else:
        station_id = None
    if variable_name is not None:
        db_variable = db.get_variable_by_name(db_session, variable_name)
        if db_variable is not None:
            variable_id = db_variable.id
        else:
            raise ValueError("Invalid variable name")
    else:
        variable_id = None
    measurements, filtered_total = db.list_seasonal_measurements(
        db_session,
        limit=list_params.limit,
        offset=list_params.offset,
        station_id_filter=station_id,
        variable_id_filter=variable_id,
        season_filter=season,
        include_total=True,
    )
    _, unfiltered_total = db.list_seasonal_measurements(
        db_session, limit=1, offset=0, include_total=True
    )
    return observations.SeasonalMeasurementList.from_items(
        measurements,
        request,
        limit=list_params.limit,
        offset=list_params.offset,
        filtered_total=filtered_total,
        unfiltered_total=unfiltered_total,
    )


@router.get(
    "/seasonal-measurements/{seasonal_measurement_id}",
    response_model=observations.SeasonalMeasurementReadListItem,
)
def get_seasonal_measurement(
    request: Request,
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    seasonal_measurement_id: pydantic.UUID4,
):
    db_measurement = db.get_seasonal_measurement(db_session, seasonal_measurement_id)
    return observations.SeasonalMeasurementReadListItem.from_db_instance(
        db_measurement, request
    )


@router.get("/yearly-measurements", response_model=observations.YearlyMeasurementList)
def list_yearly_measurements(
    request: Request,
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    list_params: Annotated[dependencies.CommonListFilterParameters, Depends()],
    station_code: str | None = None,
    variable_name: str | None = None,
):
    """List known yearly measurements."""
    if station_code is not None:
        db_station = db.get_station_by_code(db_session, station_code)
        if db_station is not None:
            station_id = db_station.id
        else:
            raise ValueError("Invalid station code")
    else:
        station_id = None
    if variable_name is not None:
        db_variable = db.get_variable_by_name(db_session, variable_name)
        if db_variable is not None:
            variable_id = db_variable.id
        else:
            raise ValueError("Invalid variable name")
    else:
        variable_id = None
    measurements, filtered_total = db.list_yearly_measurements(
        db_session,
        limit=list_params.limit,
        offset=list_params.offset,
        station_id_filter=station_id,
        variable_id_filter=variable_id,
        include_total=True,
    )
    _, unfiltered_total = db.list_yearly_measurements(
        db_session, limit=1, offset=0, include_total=True
    )
    return observations.YearlyMeasurementList.from_items(
        measurements,
        request,
        limit=list_params.limit,
        offset=list_params.offset,
        filtered_total=filtered_total,
        unfiltered_total=unfiltered_total,
    )


@router.get(
    "/yearly-measurements/{yearly_measurement_id}",
    response_model=observations.YearlyMeasurementReadListItem,
)
def get_yearly_measurement(
    request: Request,
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    yearly_measurement_id: pydantic.UUID4,
):
    db_measurement = db.get_yearly_measurement(db_session, yearly_measurement_id)
    return observations.YearlyMeasurementReadListItem.from_db_instance(
        db_measurement, request
    )


@router.get(
    "/time-series/{station_code}/{variable_name}/{month}", response_model=TimeSeriesList
)
def get_time_series(
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    station_code: str,
    month: Annotated[int, Path(ge=1, le=12)],
    variable_name: str,
    datetime: Optional[str] = "../..",
    smoothing: Annotated[list[base.ObservationDataSmoothingStrategy], Query()] = [  # noqa
        base.ObservationDataSmoothingStrategy.NO_SMOOTHING
    ],
    include_decade_data: bool = False,
    include_mann_kendall_trend: bool = False,
    mann_kendall_start_year: Optional[int] = None,
    mann_kendall_end_year: Optional[int] = None,
):
    if (db_station := db.get_station_by_code(db_session, station_code)) is not None:
        if (
            db_variable := db.get_variable_by_name(db_session, variable_name)
        ) is not None:
            if include_mann_kendall_trend:
                try:
                    mann_kendall = base.MannKendallParameters(
                        start_year=mann_kendall_start_year,
                        end_year=mann_kendall_end_year,
                    )
                except pydantic.ValidationError as err:
                    error_dict = json.loads(err.json())
                    raise HTTPException(status_code=400, detail=error_dict)
            else:
                mann_kendall = None
            try:
                observation_series = operations.get_observation_time_series(
                    session=db_session,
                    variable=db_variable,
                    station=db_station,
                    month=month,
                    temporal_range=datetime,
                    smoothing_strategies=smoothing,
                    include_decade_data=include_decade_data,
                    mann_kendall_parameters=mann_kendall,
                )
            except ValueError as err:
                raise HTTPException(status_code=400, detail=str(err))
            else:
                series = []
                for obs_series_info, pd_series_stuff in observation_series.items():
                    smoothing_strategy, derived_series = obs_series_info
                    pd_series, pd_series_info = pd_series_stuff
                    processed_series = TimeSeries.from_observation_series(
                        series=pd_series,
                        variable=db_variable,
                        smoothing_strategy=smoothing_strategy,
                        extra_info=pd_series_info,
                        derived_series=derived_series,
                    )
                    series.append(processed_series)
                return TimeSeriesList(series=series)
        else:
            raise HTTPException(status_code=400, detail="Invalid variable identifier")
    else:
        raise HTTPException(status_code=400, detail="Invalid station identifier")


def _serialize_dataframe(
    df: pd.DataFrame,
    exclude_series_name_pattern: str | None = None,
    info: dict[str, str] | None = None,
) -> list[TimeSeries]:
    series = []
    for series_name, series_measurements in df.to_dict().items():
        if (
            exclude_series_name_pattern is None
            or exclude_series_name_pattern not in series_name
        ):
            measurements = []
            for timestamp, value in series_measurements.items():
                if not math.isnan(value):
                    measurements.append(TimeSeriesItem(value=value, datetime=timestamp))
            series.append(TimeSeries(name=series_name, values=measurements, info=info))
    return series
