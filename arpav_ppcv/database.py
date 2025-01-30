"""Database utilities."""

import datetime as dt
import itertools
import logging
import uuid
from typing import (
    Optional,
    Sequence,
)

import geohashr
import geojson_pydantic
import shapely
import shapely.io
import sqlalchemy.exc
import sqlmodel
from geoalchemy2.shape import from_shape
from sqlalchemy import func

from . import (
    config,
    exceptions,
)
from .schemas import (
    base,
    climaticindicators,
    coverages,
    dataseries,
    municipalities,
    observations,
    static,
)

logger = logging.getLogger(__name__)

_DB_ENGINE = None
_TEST_DB_ENGINE = None


def get_engine(settings: config.ArpavPpcvSettings, use_test_db: Optional[bool] = False):
    # This function implements caching of the sqlalchemy engine, relying on the
    # value of the module global `_DB_ENGINE` variable. This is done in order to
    # - reuse the same database engine throughout the lifecycle of the application
    # - provide an opportunity to clear the cache when needed (e.g.: in the fastapi
    # lifespan function)
    #
    # Note: this function cannot use the `functools.cache` decorator because
    # the `settings` parameter is not hashable
    if use_test_db:
        global _TEST_DB_ENGINE
        if _TEST_DB_ENGINE is None:
            _TEST_DB_ENGINE = sqlmodel.create_engine(
                settings.test_db_dsn.unicode_string(),
                echo=True if settings.verbose_db_logs else False,
            )
        result = _TEST_DB_ENGINE
    else:
        global _DB_ENGINE
        if _DB_ENGINE is None:
            _DB_ENGINE = sqlmodel.create_engine(
                settings.db_dsn.unicode_string(),
                echo=True if settings.verbose_db_logs else False,
            )
        result = _DB_ENGINE
    return result


# def create_variable(
#     session: sqlmodel.Session, variable_create: observations.VariableCreate
# ) -> observations.Variable:
#     """Create a new variable."""
#     db_variable = observations.Variable(**variable_create.model_dump())
#     session.add(db_variable)
#     try:
#         session.commit()
#     except sqlalchemy.exc.DBAPIError:
#         raise
#     else:
#         session.refresh(db_variable)
#         return db_variable
#
#
# def create_many_variables(
#     session: sqlmodel.Session,
#     variables_to_create: Sequence[observations.VariableCreate],
# ) -> list[observations.Variable]:
#     """Create several variables."""
#     db_records = []
#     for variable_create in variables_to_create:
#         db_variable = observations.Variable(**variable_create.model_dump())
#         db_records.append(db_variable)
#         session.add(db_variable)
#     try:
#         session.commit()
#     except sqlalchemy.exc.DBAPIError:
#         raise
#     else:
#         for db_record in db_records:
#             session.refresh(db_record)
#         return db_records
#
#
# def get_variable(
#     session: sqlmodel.Session, variable_id: uuid.UUID
# ) -> Optional[observations.Variable]:
#     return session.get(observations.Variable, variable_id)
#
#
# def get_variable_by_name(
#     session: sqlmodel.Session, variable_name: str
# ) -> Optional[observations.Variable]:
#     """Get a variable by its name.
#
#     Since a variable name is unique, it can be used to uniquely identify a variable.
#     """
#     return session.exec(
#         sqlmodel.select(observations.Variable).where(
#             observations.Variable.name == variable_name
#         )
#     ).first()
#
#
# def update_variable(
#     session: sqlmodel.Session,
#     db_variable: observations.Variable,
#     variable_update: observations.VariableUpdate,
# ) -> observations.Variable:
#     """Update a variable."""
#     data_ = variable_update.model_dump(exclude_unset=True)
#     for key, value in data_.items():
#         setattr(db_variable, key, value)
#     session.add(db_variable)
#     session.commit()
#     session.refresh(db_variable)
#     return db_variable
#
#
# def delete_variable(session: sqlmodel.Session, variable_id: uuid.UUID) -> None:
#     """Delete a variable."""
#     db_variable = get_variable(session, variable_id)
#     if db_variable is not None:
#         session.delete(db_variable)
#         session.commit()
#     else:
#         raise RuntimeError("Variable not found")
#
#
# def list_variables(
#     session: sqlmodel.Session,
#     *,
#     limit: int = 20,
#     offset: int = 0,
#     include_total: bool = False,
#     name_filter: Optional[str] = None,
# ) -> tuple[Sequence[observations.Variable], Optional[int]]:
#     """List existing variables."""
#     statement = sqlmodel.select(observations.Variable).order_by(
#         observations.Variable.name
#     )
#     if name_filter is not None:
#         statement = _add_substring_filter(
#             statement, name_filter, observations.Variable.name
#         )
#     items = session.exec(statement.offset(offset).limit(limit)).all()
#     num_items = _get_total_num_records(session, statement) if include_total else None
#     return items, num_items
#
#
# def collect_all_variables(
#     session: sqlmodel.Session,
# ) -> Sequence[observations.Variable]:
#     _, num_total = list_variables(session, limit=1, include_total=True)
#     result, _ = list_variables(session, limit=num_total, include_total=False)
#     return result


# def create_station(
#     session: sqlmodel.Session, station_create: observations.StationCreate
# ) -> observations.Station:
#     """Create a new station."""
#     geom = shapely.io.from_geojson(station_create.geom.model_dump_json())
#     wkbelement = from_shape(geom)
#     db_station = observations.Station(
#         **station_create.model_dump(exclude={"geom"}),
#         geom=wkbelement,
#     )
#     session.add(db_station)
#     try:
#         session.commit()
#     except sqlalchemy.exc.DBAPIError:
#         raise
#     else:
#         session.refresh(db_station)
#         return db_station
#
#
# def create_many_stations(
#     session: sqlmodel.Session,
#     stations_to_create: Sequence[observations.StationCreate],
# ) -> list[observations.Station]:
#     """Create several stations."""
#     db_records = []
#     for station_create in stations_to_create:
#         geom = shapely.io.from_geojson(station_create.geom.model_dump_json())
#         wkbelement = from_shape(geom)
#         db_station = observations.Station(
#             **station_create.model_dump(exclude={"geom"}),
#             geom=wkbelement,
#         )
#         db_records.append(db_station)
#         session.add(db_station)
#     try:
#         session.commit()
#     except sqlalchemy.exc.DBAPIError:
#         raise
#     else:
#         for db_record in db_records:
#             session.refresh(db_record)
#         return db_records
#
#
# def get_station(
#     session: sqlmodel.Session, station_id: uuid.UUID
# ) -> Optional[observations.Station]:
#     return session.get(observations.Station, station_id)
#
#
# def get_station_by_code(
#     session: sqlmodel.Session, station_code: str
# ) -> Optional[observations.Station]:
#     """Get a station by its code.
#
#     Since a station code is unique, it can be used to uniquely identify a station.
#     """
#     return session.exec(
#         sqlmodel.select(observations.Station).where(
#             observations.Station.code == station_code
#         )
#     ).first()
#
#
# def update_station(
#     session: sqlmodel.Session,
#     db_station: observations.Station,
#     station_update: observations.StationUpdate,
# ) -> observations.Station:
#     """Update a station."""
#     geom = from_shape(shapely.io.from_geojson(station_update.geom.model_dump_json()))
#     other_data = station_update.model_dump(exclude={"geom"}, exclude_unset=True)
#     data = {**other_data, "geom": geom}
#     for key, value in data.items():
#         setattr(db_station, key, value)
#     session.add(db_station)
#     session.commit()
#     session.refresh(db_station)
#     return db_station
#
#
# def delete_station(session: sqlmodel.Session, station_id: uuid.UUID) -> None:
#     """Delete a station."""
#     db_station = get_station(session, station_id)
#     if db_station is not None:
#         session.delete(db_station)
#         session.commit()
#     else:
#         raise RuntimeError("Station not found")
#
#
# def list_stations(
#     session: sqlmodel.Session,
#     *,
#     limit: int = 20,
#     offset: int = 0,
#     include_total: bool = False,
#     name_filter: Optional[str] = None,
#     polygon_intersection_filter: shapely.Polygon = None,
#     variable_id_filter: Optional[uuid.UUID] = None,
#     variable_aggregation_type: Optional[
#         base.ObservationAggregationType
#     ] = base.ObservationAggregationType.SEASONAL,
# ) -> tuple[Sequence[observations.Station], Optional[int]]:
#     """List existing stations.
#
#     The ``polygon_intersection_filter`` parameter is expected to be a polygon
#     geometry in the EPSG:4326 CRS.
#     """
#     statement = sqlmodel.select(observations.Station).order_by(
#         observations.Station.code
#     )
#     if name_filter is not None:
#         statement = _add_substring_filter(
#             statement, name_filter, observations.Station.name
#         )
#     if polygon_intersection_filter is not None:
#         statement = statement.where(
#             func.ST_Intersects(
#                 observations.Station.geom,
#                 func.ST_GeomFromWKB(
#                     shapely.io.to_wkb(polygon_intersection_filter), 4326
#                 ),
#             )
#         )
#     if all((variable_id_filter, variable_aggregation_type)):
#         if variable_aggregation_type == base.ObservationAggregationType.MONTHLY:
#             instance_class = observations.MonthlyMeasurement
#         elif variable_aggregation_type == base.ObservationAggregationType.SEASONAL:
#             instance_class = observations.SeasonalMeasurement
#         elif variable_aggregation_type == base.ObservationAggregationType.YEARLY:
#             instance_class = observations.YearlyMeasurement
#         else:
#             raise RuntimeError(
#                 f"variable filtering for {variable_aggregation_type} is not supported"
#             )
#         statement = (
#             statement.join(instance_class)
#             .join(observations.Variable)
#             .where(observations.Variable.id == variable_id_filter)
#             .distinct()
#         )
#
#     else:
#         logger.warning(
#             "Did not perform variable filter as not all related parameters have been "
#             "provided"
#         )
#     items = session.exec(statement.offset(offset).limit(limit)).all()
#     num_items = _get_total_num_records(session, statement) if include_total else None
#     return items, num_items
#
#
# def collect_all_stations(
#     session: sqlmodel.Session,
#     polygon_intersection_filter: shapely.Polygon = None,
# ) -> Sequence[observations.Station]:
#     """Collect all stations.
#
#     The ``polygon_intersetion_filter`` parameter is expected to be a polygon
#     geometry in the EPSG:4326 CRS.
#     """
#     _, num_total = list_stations(
#         session,
#         limit=1,
#         include_total=True,
#         polygon_intersection_filter=polygon_intersection_filter,
#     )
#     result, _ = list_stations(
#         session,
#         limit=num_total,
#         include_total=False,
#         polygon_intersection_filter=polygon_intersection_filter,
#     )
#     return result


# def create_monthly_measurement(
#     session: sqlmodel.Session,
#     monthly_measurement_create: observations.MonthlyMeasurementCreate,
# ) -> observations.MonthlyMeasurement:
#     """Create a new monthly measurement."""
#     db_monthly_measurement = observations.MonthlyMeasurement(
#         **monthly_measurement_create.model_dump()
#     )
#     session.add(db_monthly_measurement)
#     try:
#         session.commit()
#     except sqlalchemy.exc.DBAPIError:
#         raise
#     else:
#         session.refresh(db_monthly_measurement)
#         return db_monthly_measurement
#
#
# def create_many_monthly_measurements(
#     session: sqlmodel.Session,
#     monthly_measurements_to_create: Sequence[observations.MonthlyMeasurementCreate],
# ) -> list[observations.MonthlyMeasurement]:
#     """Create several monthly measurements."""
#     db_records = []
#     for monthly_measurement_create in monthly_measurements_to_create:
#         db_monthly_measurement = observations.MonthlyMeasurement(
#             station_id=monthly_measurement_create.station_id,
#             variable_id=monthly_measurement_create.variable_id,
#             value=monthly_measurement_create.value,
#             date=monthly_measurement_create.date,
#         )
#         db_records.append(db_monthly_measurement)
#         session.add(db_monthly_measurement)
#     try:
#         session.commit()
#     except sqlalchemy.exc.DBAPIError:
#         raise
#     else:
#         for db_record in db_records:
#             session.refresh(db_record)
#         return db_records
#
#
# def get_monthly_measurement(
#     session: sqlmodel.Session, monthly_measurement_id: uuid.UUID
# ) -> Optional[observations.MonthlyMeasurement]:
#     return session.get(observations.MonthlyMeasurement, monthly_measurement_id)
#
#
# def delete_monthly_measurement(
#     session: sqlmodel.Session, monthly_measurement_id: uuid.UUID
# ) -> None:
#     """Delete a monthly_measurement."""
#     db_monthly_measurement = get_monthly_measurement(session, monthly_measurement_id)
#     if db_monthly_measurement is not None:
#         session.delete(db_monthly_measurement)
#         session.commit()
#     else:
#         raise RuntimeError("Monthly measurement not found")
#
#
# def list_monthly_measurements(
#     session: sqlmodel.Session,
#     *,
#     limit: int = 20,
#     offset: int = 0,
#     station_id_filter: Optional[uuid.UUID] = None,
#     climatic_indicator_id_filter: Optional[int] = None,
#     month_filter: Optional[int] = None,
#     include_total: bool = False,
# ) -> tuple[Sequence[observations.MonthlyMeasurement], Optional[int]]:
#     """List existing monthly measurements."""
#     statement = sqlmodel.select(observations.MonthlyMeasurement).order_by(
#         observations.MonthlyMeasurement.date
#     )
#     if station_id_filter is not None:
#         statement = statement.where(
#             observations.MonthlyMeasurement.station_id == station_id_filter
#         )
#     if climatic_indicator_id_filter is not None:
#         statement = statement.where(
#             observations.MonthlyMeasurement.climatic_indicator_id
#             == climatic_indicator_id_filter
#         )
#     if month_filter is not None:
#         statement = statement.where(
#             sqlmodel.func.extract("MONTH", observations.MonthlyMeasurement.date)
#             == month_filter
#         )
#     items = session.exec(statement.offset(offset).limit(limit)).all()
#     num_items = _get_total_num_records(session, statement) if include_total else None
#     return items, num_items
#
#
# def collect_all_monthly_measurements(
#     session: sqlmodel.Session,
#     *,
#     station_id_filter: Optional[uuid.UUID] = None,
#     climatic_indicator_id_filter: Optional[int] = None,
#     month_filter: Optional[int] = None,
# ) -> Sequence[observations.MonthlyMeasurement]:
#     _, num_total = list_monthly_measurements(
#         session,
#         limit=1,
#         station_id_filter=station_id_filter,
#         climatic_indicator_id_filter=climatic_indicator_id_filter,
#         month_filter=month_filter,
#         include_total=True,
#     )
#     result, _ = list_monthly_measurements(
#         session,
#         limit=num_total,
#         station_id_filter=station_id_filter,
#         climatic_indicator_id_filter=climatic_indicator_id_filter,
#         month_filter=month_filter,
#         include_total=False,
#     )
#     return result
#
#
# def create_seasonal_measurement(
#     session: sqlmodel.Session,
#     measurement_create: observations.SeasonalMeasurementCreate,
# ) -> observations.SeasonalMeasurement:
#     """Create a new seasonal measurement."""
#     db_measurement = observations.SeasonalMeasurement(**measurement_create.model_dump())
#     session.add(db_measurement)
#     try:
#         session.commit()
#     except sqlalchemy.exc.DBAPIError:
#         raise
#     else:
#         session.refresh(db_measurement)
#         return db_measurement
#
#
# def create_many_seasonal_measurements(
#     session: sqlmodel.Session,
#     measurements_to_create: Sequence[observations.SeasonalMeasurementCreate],
# ) -> list[observations.SeasonalMeasurement]:
#     """Create several seasonal measurements."""
#     db_records = []
#     for measurement_create in measurements_to_create:
#         db_measurement = observations.SeasonalMeasurement(
#             **measurement_create.model_dump()
#         )
#         db_records.append(db_measurement)
#         session.add(db_measurement)
#     try:
#         session.commit()
#     except sqlalchemy.exc.DBAPIError:
#         raise
#     else:
#         for db_record in db_records:
#             session.refresh(db_record)
#         return db_records
#
#
# def get_seasonal_measurement(
#     session: sqlmodel.Session, measurement_id: uuid.UUID
# ) -> Optional[observations.SeasonalMeasurement]:
#     return session.get(observations.SeasonalMeasurement, measurement_id)
#
#
# def delete_seasonal_measurement(
#     session: sqlmodel.Session, measurement_id: uuid.UUID
# ) -> None:
#     """Delete a seasonal measurement."""
#     db_measurement = get_seasonal_measurement(session, measurement_id)
#     if db_measurement is not None:
#         session.delete(db_measurement)
#         session.commit()
#     else:
#         raise RuntimeError("Seasonal measurement not found")
#
#
# def list_seasonal_measurements(
#     session: sqlmodel.Session,
#     *,
#     limit: int = 20,
#     offset: int = 0,
#     station_id_filter: Optional[uuid.UUID] = None,
#     climatic_indicator_id_filter: Optional[int] = None,
#     season_filter: Optional[base.Season] = None,
#     include_total: bool = False,
# ) -> tuple[Sequence[observations.SeasonalMeasurement], Optional[int]]:
#     """List existing seasonal measurements."""
#     statement = sqlmodel.select(observations.SeasonalMeasurement).order_by(
#         observations.SeasonalMeasurement.year
#     )
#     if station_id_filter is not None:
#         statement = statement.where(
#             observations.SeasonalMeasurement.station_id == station_id_filter
#         )
#     if climatic_indicator_id_filter is not None:
#         statement = statement.where(
#             observations.SeasonalMeasurement.climatic_indicator_id
#             == climatic_indicator_id_filter
#         )
#     if season_filter is not None:
#         statement = statement.where(
#             observations.SeasonalMeasurement.season == season_filter
#         )
#     items = session.exec(statement.offset(offset).limit(limit)).all()
#     num_items = _get_total_num_records(session, statement) if include_total else None
#     return items, num_items
#
#
# def collect_all_seasonal_measurements(
#     session: sqlmodel.Session,
#     *,
#     station_id_filter: Optional[uuid.UUID] = None,
#     climatic_indicator_id_filter: Optional[int] = None,
#     season_filter: Optional[base.Season] = None,
# ) -> Sequence[observations.SeasonalMeasurement]:
#     _, num_total = list_seasonal_measurements(
#         session,
#         limit=1,
#         station_id_filter=station_id_filter,
#         climatic_indicator_id_filter=climatic_indicator_id_filter,
#         season_filter=season_filter,
#         include_total=True,
#     )
#     result, _ = list_seasonal_measurements(
#         session,
#         limit=num_total,
#         station_id_filter=station_id_filter,
#         climatic_indicator_id_filter=climatic_indicator_id_filter,
#         season_filter=season_filter,
#         include_total=False,
#     )
#     return result
#
#
# def create_yearly_measurement(
#     session: sqlmodel.Session, measurement_create: observations.YearlyMeasurementCreate
# ) -> observations.YearlyMeasurement:
#     """Create a new yearly measurement."""
#     db_measurement = observations.YearlyMeasurement(**measurement_create.model_dump())
#     session.add(db_measurement)
#     try:
#         session.commit()
#     except sqlalchemy.exc.DBAPIError:
#         raise
#     else:
#         session.refresh(db_measurement)
#         return db_measurement
#
#
# def create_many_yearly_measurements(
#     session: sqlmodel.Session,
#     measurements_to_create: Sequence[observations.YearlyMeasurementCreate],
# ) -> list[observations.YearlyMeasurement]:
#     """Create several yearly measurements."""
#     db_records = []
#     for measurement_create in measurements_to_create:
#         db_measurement = observations.YearlyMeasurement(
#             **measurement_create.model_dump()
#         )
#         db_records.append(db_measurement)
#         session.add(db_measurement)
#     try:
#         session.commit()
#     except sqlalchemy.exc.DBAPIError:
#         raise
#     else:
#         for db_record in db_records:
#             session.refresh(db_record)
#         return db_records
#
#
# def get_yearly_measurement(
#     session: sqlmodel.Session, measurement_id: uuid.UUID
# ) -> Optional[observations.YearlyMeasurement]:
#     return session.get(observations.YearlyMeasurement, measurement_id)
#
#
# def delete_yearly_measurement(
#     session: sqlmodel.Session, measurement_id: uuid.UUID
# ) -> None:
#     """Delete a yearly measurement."""
#     db_measurement = get_yearly_measurement(session, measurement_id)
#     if db_measurement is not None:
#         session.delete(db_measurement)
#         session.commit()
#     else:
#         raise RuntimeError("Yearly measurement not found")
#
#
# def list_yearly_measurements(
#     session: sqlmodel.Session,
#     *,
#     limit: int = 20,
#     offset: int = 0,
#     station_id_filter: Optional[uuid.UUID] = None,
#     climatic_indicator_id_filter: Optional[int] = None,
#     include_total: bool = False,
# ) -> tuple[Sequence[observations.YearlyMeasurement], Optional[int]]:
#     """List existing yearly measurements."""
#     statement = sqlmodel.select(observations.YearlyMeasurement).order_by(
#         observations.YearlyMeasurement.year
#     )
#     if station_id_filter is not None:
#         statement = statement.where(
#             observations.YearlyMeasurement.station_id == station_id_filter
#         )
#     if climatic_indicator_id_filter is not None:
#         statement = statement.where(
#             observations.YearlyMeasurement.climatic_indicator_id
#             == climatic_indicator_id_filter
#         )
#     items = session.exec(statement.offset(offset).limit(limit)).all()
#     num_items = _get_total_num_records(session, statement) if include_total else None
#     return items, num_items
#
#
# def collect_all_yearly_measurements(
#     session: sqlmodel.Session,
#     *,
#     station_id_filter: Optional[uuid.UUID] = None,
#     climatic_indicator_id_filter: Optional[int] = None,
# ) -> Sequence[observations.YearlyMeasurement]:
#     _, num_total = list_yearly_measurements(
#         session,
#         limit=1,
#         station_id_filter=station_id_filter,
#         climatic_indicator_id_filter=climatic_indicator_id_filter,
#         include_total=True,
#     )
#     result, _ = list_yearly_measurements(
#         session,
#         limit=num_total,
#         station_id_filter=station_id_filter,
#         climatic_indicator_id_filter=climatic_indicator_id_filter,
#         include_total=False,
#     )
#     return result


def get_configuration_parameter_value(
    session: sqlmodel.Session, configuration_parameter_value_id: uuid.UUID
) -> Optional[coverages.ConfigurationParameterValue]:
    return session.get(
        coverages.ConfigurationParameterValue, configuration_parameter_value_id
    )


def get_configuration_parameter_value_by_names(
    session: sqlmodel.Session,
    parameter_name: str,
    value_name: str,
) -> Optional[coverages.ConfigurationParameterValue]:
    """Get configuration parameter value by name of parameter and name of value."""
    return session.exec(
        sqlmodel.select(coverages.ConfigurationParameterValue)
        .join(coverages.ConfigurationParameter)
        .where(
            coverages.ConfigurationParameter.name == parameter_name,
            coverages.ConfigurationParameterValue.name == value_name,
        )
    ).first()


def list_configuration_parameter_values(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    used_by_coverage_configuration: coverages.CoverageConfiguration | None = None,
) -> tuple[Sequence[coverages.ConfigurationParameterValue], Optional[int]]:
    """List existing configuration parameters."""
    statement = sqlmodel.select(coverages.ConfigurationParameterValue).order_by(
        coverages.ConfigurationParameterValue.name
    )
    if used_by_coverage_configuration is not None:
        statement = (
            statement.join(coverages.ConfigurationParameterPossibleValue)
            .join(coverages.CoverageConfiguration)
            .where(
                coverages.CoverageConfiguration.id == used_by_coverage_configuration.id
            )
        )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = _get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_configuration_parameter_values(
    session: sqlmodel.Session,
    used_by_coverage_configuration: coverages.CoverageConfiguration | None = None,
) -> Sequence[coverages.ConfigurationParameterValue]:
    _, num_total = list_configuration_parameter_values(
        session,
        limit=1,
        include_total=True,
        used_by_coverage_configuration=used_by_coverage_configuration,
    )
    result, _ = list_configuration_parameter_values(
        session,
        limit=num_total,
        include_total=False,
        used_by_coverage_configuration=used_by_coverage_configuration,
    )
    return result


def get_configuration_parameter(
    session: sqlmodel.Session, configuration_parameter_id: uuid.UUID
) -> Optional[coverages.ConfigurationParameter]:
    return session.get(coverages.ConfigurationParameter, configuration_parameter_id)


def get_configuration_parameter_by_name(
    session: sqlmodel.Session, configuration_parameter_name: str
) -> Optional[coverages.ConfigurationParameter]:
    """Get a configuration parameter by its name.

    Since a configuration parameter's name is unique, it can be used to uniquely
    identify it.
    """
    return session.exec(
        sqlmodel.select(coverages.ConfigurationParameter).where(
            coverages.ConfigurationParameter.name == configuration_parameter_name
        )
    ).first()


def list_configuration_parameters(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    name_filter: str | None = None,
) -> tuple[Sequence[coverages.ConfigurationParameter], Optional[int]]:
    """List existing configuration parameters."""
    statement = sqlmodel.select(coverages.ConfigurationParameter).order_by(
        coverages.ConfigurationParameter.name
    )
    if name_filter is not None:
        statement = _add_substring_filter(
            statement, name_filter, coverages.ConfigurationParameter.name
        )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = _get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_configuration_parameters(
    session: sqlmodel.Session,
) -> Sequence[coverages.ConfigurationParameter]:
    _, num_total = list_configuration_parameters(session, limit=1, include_total=True)
    result, _ = list_configuration_parameters(
        session, limit=num_total, include_total=False
    )
    return result


def create_configuration_parameter_value(
    session: sqlmodel.Session,
    parameter_value: coverages.ConfigurationParameterValueCreate,
) -> coverages.ConfigurationParameterValue:
    param_name = parameter_value.name or _slugify_internal_value(
        parameter_value.internal_value
    )
    db_param_value = coverages.ConfigurationParameterValue(
        **parameter_value.model_dump(exclude={"name"}),
        name=param_name,
    )
    session.add(db_param_value)
    session.commit()
    session.refresh(db_param_value)
    return db_param_value


def create_configuration_parameter(
    session: sqlmodel.Session,
    configuration_parameter_create: coverages.ConfigurationParameterCreate,
) -> coverages.ConfigurationParameter:
    to_refresh = []
    db_configuration_parameter = coverages.ConfigurationParameter(
        name=configuration_parameter_create.name,
        display_name_english=configuration_parameter_create.display_name_english,
        display_name_italian=configuration_parameter_create.display_name_italian,
        description_english=configuration_parameter_create.description_english,
        description_italian=configuration_parameter_create.description_italian,
    )
    to_refresh.append(db_configuration_parameter)
    for allowed in configuration_parameter_create.allowed_values:
        db_conf_param_value = coverages.ConfigurationParameterValue(
            internal_value=allowed.internal_value,
            name=allowed.name or _slugify_internal_value(allowed.internal_value),
            display_name_english=allowed.display_name_english,
            display_name_italian=allowed.display_name_italian,
            description_english=allowed.description_english,
            description_italian=allowed.description_italian,
            sort_order=allowed.sort_order,
        )
        db_configuration_parameter.allowed_values.append(db_conf_param_value)
        to_refresh.append(db_conf_param_value)
    session.add(db_configuration_parameter)
    session.commit()
    for item in to_refresh:
        session.refresh(item)
    return db_configuration_parameter


def update_configuration_parameter(
    session: sqlmodel.Session,
    db_configuration_parameter: coverages.ConfigurationParameter,
    configuration_parameter_update: coverages.ConfigurationParameterUpdate,
) -> coverages.ConfigurationParameter:
    """Update a configuration parameter."""
    to_refresh = []
    # account for allowed values being: added/modified/deleted
    for existing_allowed_value in db_configuration_parameter.allowed_values:
        has_been_requested_to_remove = existing_allowed_value.id not in [
            i.id for i in configuration_parameter_update.allowed_values
        ]
        if has_been_requested_to_remove:
            session.delete(existing_allowed_value)
    for av in configuration_parameter_update.allowed_values:
        if av.id is None:
            # this is a new allowed value, need to create it
            db_allowed_value = coverages.ConfigurationParameterValue(
                internal_value=av.internal_value,
                name=av.name or _slugify_internal_value(av.internal_value),
                display_name_english=av.display_name_english,
                display_name_italian=av.display_name_italian,
                description_english=av.description_english,
                description_italian=av.description_italian,
                sort_order=av.sort_order or 0,
            )
            db_configuration_parameter.allowed_values.append(db_allowed_value)
        else:
            # this is an existing allowed value, lets update
            db_allowed_value = get_configuration_parameter_value(session, av.id)
            for prop, value in av.model_dump(
                exclude={"id"}, exclude_none=True, exclude_unset=True
            ).items():
                setattr(db_allowed_value, prop, value)
        session.add(db_allowed_value)
        to_refresh.append(db_allowed_value)
    data_ = configuration_parameter_update.model_dump(
        exclude={"allowed_values"}, exclude_unset=True, exclude_none=True
    )
    for key, value in data_.items():
        setattr(db_configuration_parameter, key, value)
    session.add(db_configuration_parameter)
    to_refresh.append(db_configuration_parameter)
    session.commit()
    for item in to_refresh:
        session.refresh(item)
    return db_configuration_parameter


def get_coverage_configuration(
    session: sqlmodel.Session, coverage_configuration_id: uuid.UUID
) -> Optional[coverages.CoverageConfiguration]:
    return session.get(coverages.CoverageConfiguration, coverage_configuration_id)


def get_coverage_configuration_by_name(
    session: sqlmodel.Session, coverage_configuration_name: str
) -> Optional[coverages.CoverageConfiguration]:
    """Get a coverage configuration by its name.

    Since a coverage configuration name is unique, it can be used to uniquely
    identify it.
    """
    return session.exec(
        sqlmodel.select(coverages.CoverageConfiguration).where(
            coverages.CoverageConfiguration.name == coverage_configuration_name
        )
    ).first()


def get_forecast_coverage_data_series(session: sqlmodel.Session, identifier: str):
    # a forecast data series is always identified by a string like:
    # {forecast_coverage_identifier}-{series_identifier}, where {series_identifier} is:
    # {dataset_type}-{wkt_location}-{temporal_range_start}-{temporal_range_end}-{smoothing_identifier}
    all_parts = identifier.split("-")
    forecast_coverage_identifier = "-".join(all_parts[:-5])
    forecast_coverage = get_forecast_coverage(session, forecast_coverage_identifier)
    if forecast_coverage is None:
        raise exceptions.InvalidForecastCoverageDataSeriesIdentifierError(
            f"forecast coverage {forecast_coverage_identifier!r} does not exist"
        )
    raw_ds_type, raw_location, raw_start, raw_end, raw_smoothing_strategy = identifier
    try:
        dataset_type = static.ForecastDatasetType(raw_ds_type)
    except ValueError:
        raise exceptions.InvalidForecastCoverageDataSeriesIdentifierError(
            f"dataset type {raw_ds_type} does not exist"
        )
    try:
        location = shapely.Point(geohashr.decode(raw_location))
    except ValueError:
        raise exceptions.InvalidForecastCoverageDataSeriesIdentifierError(
            f"location {raw_location} is invalid"
        )
    try:
        start = (
            dt.date(int(raw_start[:4]), int(raw_start[4:6]), int(raw_start[6:8]))
            if raw_start != "*"
            else None
        )
    except IndexError:
        raise exceptions.InvalidForecastCoverageDataSeriesIdentifierError(
            f"temporal range start {raw_start!r} is invalid"
        )
    try:
        end = (
            dt.date(int(raw_end[:4]), int(raw_end[4:6]), int(raw_end[6:8]))
            if raw_end != "*"
            else None
        )
    except IndexError:
        raise exceptions.InvalidForecastCoverageDataSeriesIdentifierError(
            f"temporal range start {raw_start!r} is invalid"
        )
    try:
        smoothing_strategy = base.CoverageDataSmoothingStrategy(
            raw_smoothing_strategy.upper()
        )
    except ValueError:
        raise exceptions.InvalidForecastCoverageDataSeriesIdentifierError(
            f"smoothing strategy {raw_smoothing_strategy} does not exist"
        )
    return dataseries.ForecastDataSeries(
        forecast_coverage=forecast_coverage,
        dataset_type=dataset_type,
        smoothing_strategy=smoothing_strategy,
        temporal_start=start,
        temporal_end=end,
        location=location,
    )


def get_forecast_coverage(
    session: sqlmodel.Session, identifier: str
) -> Optional[coverages.ForecastCoverageInternal]:
    parts = identifier.split("-")
    time_window_name = None
    # first try to find the forecast coverage configuration using the longest
    # possible identifier, which is with seven parts...
    possible_seven_part_cov_conf_identifier = "-".join(parts[:7])
    try:
        forecast_cov_conf = get_forecast_coverage_configuration_by_identifier(
            session, possible_seven_part_cov_conf_identifier
        )
    except exceptions.ArpavError:
        forecast_cov_conf = None
    if forecast_cov_conf is not None:
        forecast_model_name = forecast_cov_conf.forecast_model_links[
            0
        ].forecast_model.name
        year_period_value = forecast_cov_conf.year_periods[0].value
        remaining_parts = parts[7:]
        scenario_value = remaining_parts[0]
        if len(remaining_parts) > 1:
            time_window_name = remaining_parts[1]
    else:
        # ... if it can't be found, then try a shorter forecast coverage
        # configuration identifier, using six parts
        possible_six_part_cov_conf_identifier = "-".join(parts[:6])
        try:
            forecast_cov_conf = get_forecast_coverage_configuration_by_identifier(
                session, possible_six_part_cov_conf_identifier
            )
        except exceptions.ArpavError:
            forecast_cov_conf = None
        if forecast_cov_conf is not None:
            remaining_parts = parts[6:]
            forecast_model_or_scenario_value, scenario_or_year_period = remaining_parts[
                :2
            ]
            if len(forecast_cov_conf.forecast_model_links) == 1:
                forecast_model_name = forecast_cov_conf.forecast_model_links[
                    0
                ].forecast_model.name
                scenario_value = forecast_model_or_scenario_value
                year_period_value = scenario_or_year_period
            elif len(forecast_cov_conf.year_periods) == 1:
                year_period_value = forecast_cov_conf.year_periods[0].value
                forecast_model_name = forecast_model_or_scenario_value
                scenario_value = scenario_or_year_period
            else:
                raise RuntimeError(
                    f"Something went wrong with the detection of this forecast "
                    f"coverage identifier: {identifier!r}"
                )
            if len(remaining_parts) > 2:
                time_window_name = remaining_parts[2]
        else:
            # ... if it still can't be found, then try the shortest possible forecast
            # coverage configuration identifier, using five parts
            possible_five_part_cov_conf_identifier = "-".join(parts[:5])
            forecast_cov_conf = get_forecast_coverage_configuration_by_identifier(
                session, possible_five_part_cov_conf_identifier
            )
            if forecast_cov_conf is not None:
                remaining_parts = parts[5:]
                (
                    forecast_model_name,
                    scenario_value,
                    year_period_value,
                ) = remaining_parts[:3]
                if len(remaining_parts) > 3:
                    time_window_name = remaining_parts[3]
            else:
                raise exceptions.InvalidForecastCoverageIdentifierError(
                    f"Could not find the forecast coverage's respective configuration "
                    f"- Tried: {possible_seven_part_cov_conf_identifier!r}, "
                    f"{possible_six_part_cov_conf_identifier!r} and "
                    f"{possible_five_part_cov_conf_identifier!r}"
                )
    return coverages.ForecastCoverageInternal(
        configuration=forecast_cov_conf,
        scenario=static.ForecastScenario(scenario_value),
        forecast_model=get_forecast_model_by_name(session, forecast_model_name),
        forecast_year_period=static.ForecastYearPeriod(year_period_value),
        forecast_time_window=(
            get_forecast_time_window_by_name(session, time_window_name)
            if time_window_name is not None
            else None
        ),
    )

    # # first try to find a longer forecast coverage configuration identifier
    # long_forecast_cov_conf_identifier = "-".join(parts[:6])
    # try:
    #     forecast_cov_conf = get_forecast_coverage_configuration_by_identifier(
    #         session, long_forecast_cov_conf_identifier
    #     )
    # except exceptions.InvalidForecastCoverageConfigurationIdentifierError:
    #     forecast_cov_conf = None
    # time_window_name = None
    # logger.debug(f"{forecast_cov_conf.identifier if forecast_cov_conf is not None else None=}")
    # if forecast_cov_conf is not None:
    #     remaining_parts = parts[6:]
    #     logger.debug(f"{remaining_parts=}")
    #     if len(forecast_cov_conf.forecast_model_links) == 1:
    #         forecast_model_name = (
    #             forecast_cov_conf.forecast_model_links[0].forecast_model.name)
    #         scenario_value, year_period_value = remaining_parts[:2]
    #     else:
    #         year_period_value = forecast_cov_conf.year_periods[0].value
    #         forecast_model_name, scenario_value = remaining_parts[:2]
    #     if len(remaining_parts) > 2:
    #         time_window_name = remaining_parts[2]
    # else:
    #     # then try a shorter forecast coverage configuration identifier
    #     short_forecast_cov_conf_identifier = "-".join(parts[:5])
    #     forecast_cov_conf = get_forecast_coverage_configuration_by_identifier(
    #         session, short_forecast_cov_conf_identifier
    #     )
    #     logger.debug(f"{forecast_cov_conf.identifier if forecast_cov_conf is not None else None=}")
    #     if forecast_cov_conf is not None:
    #         remaining_parts = parts[5:]
    #         logger.debug(f"{remaining_parts=}")
    #         forecast_model_name, scenario_value, year_period_value = remaining_parts[:3]
    #         if len(remaining_parts) > 3:
    #             time_window_name = remaining_parts[3]
    #     else:
    #         raise exceptions.InvalidForecastCoverageIdentifierError(
    #             f"Could not find a forecast coverage identifier matching either "
    #             f"{long_forecast_cov_conf_identifier!r} or "
    #             f"{short_forecast_cov_conf_identifier!r}"
    #         )
    # return coverages.ForecastCoverageInternal(
    #     configuration=forecast_cov_conf,
    #     scenario=static.ForecastScenario(scenario_value),
    #     forecast_model=get_forecast_model_by_name(session, forecast_model_name),
    #     forecast_year_period=static.ForecastYearPeriod(year_period_value),
    #     forecast_time_window=(
    #         get_forecast_time_window_by_name(session, time_window_name)
    #         if time_window_name is not None
    #         else None
    #     ),
    # )


def get_coverage(
    session: sqlmodel.Session, coverage_identifier: str
) -> Optional[coverages.CoverageInternal]:
    cov_conf_name = coverage_identifier.partition("-")[0]
    cov_conf = get_coverage_configuration_by_name(session, cov_conf_name)
    result = None
    if cov_conf is not None:
        possible_cov_ids = generate_coverage_identifiers(cov_conf)
        if coverage_identifier in possible_cov_ids:
            result = coverages.CoverageInternal(
                identifier=coverage_identifier, configuration=cov_conf
            )
    return result


def list_coverage_configurations(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    name_filter: Optional[str] = None,
    configuration_parameter_values_filter: Optional[
        list[coverages.ConfigurationParameterValue]
    ] = None,
    climatic_indicator_filter: Optional[climaticindicators.ClimaticIndicator] = None,
) -> tuple[Sequence[coverages.CoverageConfiguration], Optional[int]]:
    """List existing coverage configurations."""
    statement = sqlmodel.select(coverages.CoverageConfiguration).order_by(
        coverages.CoverageConfiguration.name
    )
    if climatic_indicator_filter is None:
        (
            configuration_parameter_values_filter,
            climatic_indicator_filter,
        ) = _replace_conf_param_filters_with_climatic_indicator(
            session, configuration_parameter_values_filter or []
        )
        if climatic_indicator_filter is not None:
            statement = statement.where(
                coverages.CoverageConfiguration.climatic_indicator_id
                == climatic_indicator_filter.id
            )
    else:
        statement = statement.where(
            coverages.CoverageConfiguration.climatic_indicator_id
            == climatic_indicator_filter.id
        )
    if name_filter is not None:
        statement = _add_substring_filter(
            statement, name_filter, coverages.CoverageConfiguration.name
        )
    if len(conf_params := configuration_parameter_values_filter or []) > 0:
        possible_values_cte = (
            sqlmodel.select(
                coverages.CoverageConfiguration.id,
                func.jsonb_agg(
                    func.json_build_object(
                        coverages.ConfigurationParameter.name,
                        coverages.ConfigurationParameterValue.name,
                    )
                ).label("possible_values"),
            )
            .join(
                coverages.ConfigurationParameterPossibleValue,
                coverages.CoverageConfiguration.id
                == coverages.ConfigurationParameterPossibleValue.coverage_configuration_id,
            )
            .join(
                coverages.ConfigurationParameterValue,
                coverages.ConfigurationParameterValue.id
                == coverages.ConfigurationParameterPossibleValue.configuration_parameter_value_id,
            )
            .join(
                coverages.ConfigurationParameter,
                coverages.ConfigurationParameter.id
                == coverages.ConfigurationParameterValue.configuration_parameter_id,
            )
            .group_by(coverages.CoverageConfiguration.id)
        ).cte("cov_conf_possible_values")
        statement = statement.join(
            possible_values_cte,
            possible_values_cte.c.id == coverages.CoverageConfiguration.id,
        )
        for conf_param_value in conf_params:
            param_name = conf_param_value.configuration_parameter.name
            param_value = conf_param_value.name
            statement = statement.where(
                func.jsonb_path_exists(
                    possible_values_cte.c.possible_values,
                    # the below expression is a fragment of SQL/JSON Path
                    # language, which represents postgresql's way of filtering a
                    # JSON array. More detail at:
                    #
                    # https://www.postgresql.org/docs/current/functions-json.html#FUNCTIONS-SQLJSON-PATH
                    #
                    # in this case it reads like:
                    # return True if the current element of the array, which is an object, has a key named
                    # `param_name` with a corresponding value of `param_value`
                    f'$[*] ? (@.{param_name} == "{param_value}")',
                )
            )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = _get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_coverage_configurations(
    session: sqlmodel.Session,
    name_filter: Optional[str] = None,
    configuration_parameter_values_filter: Optional[
        list[coverages.ConfigurationParameterValue]
    ] = None,
    climatic_indicator_filter: Optional[climaticindicators.ClimaticIndicator] = None,
) -> Sequence[coverages.CoverageConfiguration]:
    _, num_total = list_coverage_configurations(
        session,
        limit=1,
        include_total=True,
        name_filter=name_filter,
        configuration_parameter_values_filter=configuration_parameter_values_filter,
        climatic_indicator_filter=climatic_indicator_filter,
    )
    result, _ = list_coverage_configurations(
        session,
        limit=num_total,
        include_total=False,
        name_filter=name_filter,
        configuration_parameter_values_filter=configuration_parameter_values_filter,
        climatic_indicator_filter=climatic_indicator_filter,
    )
    return result


def create_coverage_configuration(
    session: sqlmodel.Session,
    coverage_configuration_create: coverages.CoverageConfigurationCreate,
) -> coverages.CoverageConfiguration:
    to_refresh = []
    db_coverage_configuration = coverages.CoverageConfiguration(
        name=coverage_configuration_create.name,
        netcdf_main_dataset_name=coverage_configuration_create.netcdf_main_dataset_name,
        wms_main_layer_name=coverage_configuration_create.wms_main_layer_name,
        wms_secondary_layer_name=coverage_configuration_create.wms_secondary_layer_name,
        thredds_url_pattern=coverage_configuration_create.thredds_url_pattern,
        climatic_indicator_id=coverage_configuration_create.climatic_indicator_id,
        uncertainty_lower_bounds_coverage_configuration_id=(
            coverage_configuration_create.uncertainty_lower_bounds_coverage_configuration_id
        ),
        uncertainty_upper_bounds_coverage_configuration_id=(
            coverage_configuration_create.uncertainty_upper_bounds_coverage_configuration_id
        ),
    )
    session.add(db_coverage_configuration)
    to_refresh.append(db_coverage_configuration)
    for (
        secondary_cov_conf_id
    ) in coverage_configuration_create.secondary_coverage_configurations_ids:
        db_secondary_cov_conf = get_coverage_configuration(
            session, secondary_cov_conf_id
        )
        db_related = coverages.RelatedCoverageConfiguration(
            main_coverage_configuration=db_coverage_configuration,
            secondary_coverage_configuration=db_secondary_cov_conf,
        )
        session.add(db_related)
        to_refresh.append(db_related)
    for possible in coverage_configuration_create.possible_values:
        db_conf_param_value = get_configuration_parameter_value(
            session, possible.configuration_parameter_value_id
        )
        if db_conf_param_value is not None:
            possible_value = coverages.ConfigurationParameterPossibleValue(
                coverage_configuration=db_coverage_configuration,
                configuration_parameter_value_id=db_conf_param_value.id,
            )
            session.add(possible_value)
            to_refresh.append(possible_value)
        else:
            raise ValueError(
                f"Configuration parameter value with id "
                f"{possible.configuration_parameter_value_id} does not exist"
            )
    session.commit()
    for item in to_refresh:
        session.refresh(item)
    return db_coverage_configuration


def update_coverage_configuration(
    session: sqlmodel.Session,
    db_coverage_configuration: coverages.CoverageConfiguration,
    coverage_configuration_update: coverages.CoverageConfigurationUpdate,
) -> coverages.CoverageConfiguration:
    """Update a coverage configuration."""
    to_refresh = []
    # account for possible values being: added/deleted
    existing_possible_values_to_keep = []
    existing_possible_values_discard = []
    for existing_possible_value in db_coverage_configuration.possible_values:
        has_been_requested_to_remove = (
            existing_possible_value.configuration_parameter_value_id
            not in [
                i.configuration_parameter_value_id
                for i in coverage_configuration_update.possible_values
            ]
        )
        if not has_been_requested_to_remove:
            existing_possible_values_to_keep.append(existing_possible_value)
        else:
            existing_possible_values_discard.append(existing_possible_value)
    db_coverage_configuration.possible_values = existing_possible_values_to_keep
    for to_discard in existing_possible_values_discard:
        session.delete(to_discard)
    for pvc in coverage_configuration_update.possible_values:
        already_possible = pvc.configuration_parameter_value_id in [
            i.configuration_parameter_value_id
            for i in db_coverage_configuration.possible_values
        ]
        if not already_possible:
            db_possible_value = coverages.ConfigurationParameterPossibleValue(
                coverage_configuration=db_coverage_configuration,
                configuration_parameter_value_id=pvc.configuration_parameter_value_id,
            )
            session.add(db_possible_value)
            to_refresh.append(db_possible_value)
    # account for related cov confs being added/deleted
    for existing_related in db_coverage_configuration.secondary_coverage_configurations:
        has_been_requested_to_remove = (
            existing_related.secondary_coverage_configuration_id
            not in [
                i
                for i in coverage_configuration_update.secondary_coverage_configurations_ids
            ]
        )
        if has_been_requested_to_remove:
            session.delete(existing_related)
    for (
        secondary_id
    ) in coverage_configuration_update.secondary_coverage_configurations_ids:
        already_related = secondary_id in [
            i.secondary_coverage_configuration_id
            for i in db_coverage_configuration.secondary_coverage_configurations
        ]
        if not already_related:
            db_secondary_cov_conf = get_coverage_configuration(session, secondary_id)
            db_related = coverages.RelatedCoverageConfiguration(
                main_coverage_configuration=db_coverage_configuration,
                secondary_coverage_configuration=db_secondary_cov_conf,
            )
            session.add(db_related)
            to_refresh.append(db_related)

    data_ = coverage_configuration_update.model_dump(
        exclude={
            "possible_values",
            "secondary_coverage_configurations_ids",
        },
        exclude_unset=True,
        exclude_none=True,
    )
    for key, value in data_.items():
        setattr(db_coverage_configuration, key, value)
    session.add(db_coverage_configuration)
    to_refresh.append(db_coverage_configuration)
    session.commit()
    for item in to_refresh:
        session.refresh(item)
    return db_coverage_configuration


def delete_coverage_configuration(
    session: sqlmodel.Session, coverage_configuration_id: uuid.UUID
) -> None:
    """Delete a coverage configuration."""
    db_coverage_configuration = get_coverage_configuration(
        session, coverage_configuration_id
    )
    if db_coverage_configuration is not None:
        session.delete(db_coverage_configuration)
        session.commit()
    else:
        raise RuntimeError("Coverage configuration not found")


def generate_forecast_coverages_from_configuration(
    forecast_coverage_configuration: coverages.ForecastCoverageConfiguration,
) -> list[coverages.ForecastCoverageInternal]:
    result = []
    to_combine = [
        forecast_coverage_configuration.scenarios,
        forecast_coverage_configuration.year_periods,
        forecast_coverage_configuration.forecast_model_links,
    ]
    has_time_window = (
        len(forecast_coverage_configuration.forecast_time_window_links) > 0
    )
    if has_time_window:
        to_combine.append(forecast_coverage_configuration.forecast_time_window_links)
    for combination in itertools.product(*to_combine):
        scenario, year_period, fm_link = combination[:3]
        tw_link = None
        if has_time_window:
            tw_link = combination[3]
        try:
            result.append(
                coverages.ForecastCoverageInternal(
                    configuration=forecast_coverage_configuration,
                    scenario=scenario,
                    forecast_model=fm_link.forecast_model,
                    forecast_year_period=year_period,
                    forecast_time_window=tw_link.forecast_time_window
                    if tw_link
                    else None,
                )
            )
        except (
            exceptions.InvalidForecastModelError,
            exceptions.InvalidForecastTimeWindowError,
        ):
            logger.exception(
                f"Could not generate forecast coverage from combination {combination}"
            )
    return result


def generate_forecast_coverages_for_other_models(
    session: sqlmodel.Session,
    forecast_coverage: coverages.ForecastCoverageInternal,
) -> list[coverages.ForecastCoverageInternal]:
    """Get a list of forecast coverages with the other forecast models.

    The implementation of this function is a bit complex because it is possible
    that forecast models for the same climatic indicator are distributed across
    multiple forecast coverage configurations.
    """

    all_forecast_models = collect_all_forecast_models(session)
    other_model_ids = [
        fm.id
        for fm in all_forecast_models
        if fm.id != forecast_coverage.forecast_model.id
    ]

    indicator = forecast_coverage.configuration.climatic_indicator
    conf_ids = set()
    for candidate_forecast_cov_conf in indicator.forecast_coverage_configurations:
        for candidate_model_link in candidate_forecast_cov_conf.forecast_model_links:
            if candidate_model_link.forecast_model_id in other_model_ids:
                # the respective forecast_cov_conf is able to generate forecast
                # coverages with this forecast model
                conf_ids.add(candidate_forecast_cov_conf.id)
    candidate_forecast_coverages = []
    for conf_id in conf_ids:
        forecast_cov_conf = get_forecast_coverage_configuration(session, conf_id)
        possible_forecast_coverages = generate_forecast_coverages_from_configuration(
            forecast_cov_conf
        )
        candidate_forecast_coverages.extend(possible_forecast_coverages)

    result = []
    for candidate in candidate_forecast_coverages:
        same_scenario = candidate.scenario == forecast_coverage.scenario
        same_year_period = (
            candidate.forecast_year_period == forecast_coverage.forecast_year_period
        )
        different_model = (
            candidate.forecast_model.id != forecast_coverage.forecast_model.id
        )
        model_already_in_result = candidate.forecast_model.id in [
            f.forecast_model.id for f in result
        ]
        if same_scenario and same_year_period and different_model:
            if not model_already_in_result:
                logger.debug(f"Adding {candidate.identifier!r} to the result...")
                result.append(candidate)
            else:
                logger.debug(
                    f"Not Adding {candidate.identifier!r} to the result because "
                    f"another forecast coverage with the same forecast model is "
                    f"already present in the result..."
                )
    return result


def generate_coverage_identifiers(
    coverage_configuration: coverages.CoverageConfiguration,
    configuration_parameter_values_filter: Optional[
        list[coverages.ConfigurationParameterValue]
    ] = None,
) -> list[str]:
    """Build list of legal coverage identifiers for a coverage configuration."""
    params_to_filter = {}
    for cpv in configuration_parameter_values_filter or []:
        values = params_to_filter.setdefault(cpv.configuration_parameter.name, [])
        values.append(cpv.name)
    conf_param_id_parts = coverage_configuration.coverage_id_pattern.split("-")[2:]
    values_to_combine = []
    for part in conf_param_id_parts:
        param_name = part.translate(str.maketrans("", "", "{}"))
        part_values = []
        for possible_value in coverage_configuration.possible_values:
            this_param_name = possible_value.configuration_parameter_value.configuration_parameter.name
            if this_param_name == param_name:
                # check if this param's value is to be filtered out or not
                this_value = possible_value.configuration_parameter_value.name
                if this_param_name in params_to_filter:
                    if this_value in params_to_filter.get(this_param_name, []):
                        part_values.append(this_value)
                else:
                    part_values.append(this_value)
        values_to_combine.append(part_values)

    allowed_identifiers = []
    for combination in itertools.product(*values_to_combine):
        dataset_id = "-".join(
            (
                coverage_configuration.name,
                coverage_configuration.climatic_indicator.identifier,
                *combination,
            )
        )
        allowed_identifiers.append(dataset_id)
    return allowed_identifiers


def list_municipality_centroids(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    polygon_intersection_filter: shapely.Polygon = None,
    name_filter: Optional[str] = None,
    province_name_filter: Optional[str] = None,
    region_name_filter: Optional[str] = None,
) -> tuple[Sequence[municipalities.MunicipalityCentroid], Optional[int]]:
    """List existing municipality centroids.

    ``polygon_intersection_filter`` parameter is expected to be express a geometry in
    the EPSG:4326 CRS.
    """
    statement = sqlmodel.select(municipalities.Municipality).order_by(
        municipalities.Municipality.name
    )
    if name_filter is not None:
        statement = _add_substring_filter(
            statement, name_filter, municipalities.Municipality.name
        )
    if province_name_filter is not None:
        statement = _add_substring_filter(
            statement, province_name_filter, municipalities.Municipality.province_name
        )
    if region_name_filter is not None:
        statement = _add_substring_filter(
            statement, region_name_filter, municipalities.Municipality.region_name
        )
    if polygon_intersection_filter is not None:
        statement = statement.where(
            func.ST_Intersects(
                municipalities.Municipality.geom,
                func.ST_GeomFromWKB(
                    shapely.io.to_wkb(polygon_intersection_filter), 4326
                ),
            )
        )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = _get_total_num_records(session, statement) if include_total else None
    return [
        municipalities.MunicipalityCentroid(
            id=i.id,
            name=i.name,
            province_name=i.province_name,
            region_name=i.region_name,
            geom=geojson_pydantic.Point(
                type="Point",
                coordinates=(i.centroid_epsg_4326_lon, i.centroid_epsg_4326_lat),
            ),
        )
        for i in items
    ], num_items


def list_municipalities(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    polygon_intersection_filter: shapely.Polygon = None,
    point_filter: shapely.Point = None,
    name_filter: Optional[str] = None,
    province_name_filter: Optional[str] = None,
    region_name_filter: Optional[str] = None,
) -> tuple[Sequence[municipalities.Municipality], Optional[int]]:
    """List existing municipalities.

    Both ``polygon_intersection_filter`` and ``point_filter`` parameters are expected
    to be a geometries in the EPSG:4326 CRS.
    """
    statement = sqlmodel.select(municipalities.Municipality).order_by(
        municipalities.Municipality.name
    )
    if name_filter is not None:
        statement = _add_substring_filter(
            statement, name_filter, municipalities.Municipality.name
        )
    if province_name_filter is not None:
        statement = _add_substring_filter(
            statement, province_name_filter, municipalities.Municipality.province_name
        )
    if region_name_filter is not None:
        statement = _add_substring_filter(
            statement, region_name_filter, municipalities.Municipality.region_name
        )
    if polygon_intersection_filter is not None:
        statement = statement.where(
            func.ST_Intersects(
                municipalities.Municipality.geom,
                func.ST_GeomFromWKB(
                    shapely.io.to_wkb(polygon_intersection_filter), 4326
                ),
            )
        )
    if point_filter is not None:
        statement = statement.where(
            func.ST_Intersects(
                municipalities.Municipality.geom,
                func.ST_GeomFromWKB(shapely.io.to_wkb(point_filter), 4326),
            )
        )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = _get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_municipalities(
    session: sqlmodel.Session,
) -> Sequence[municipalities.Municipality]:
    _, num_total = list_municipalities(session, limit=1, include_total=True)
    result, _ = list_municipalities(session, limit=num_total, include_total=False)
    return result


def create_many_municipalities(
    session: sqlmodel.Session,
    municipalities_to_create: Sequence[municipalities.MunicipalityCreate],
) -> list[municipalities.Municipality]:
    """Create several municipalities."""
    db_records = []
    for mun_create in municipalities_to_create:
        geom = shapely.io.from_geojson(mun_create.geom.model_dump_json())
        wkbelement = from_shape(geom)
        db_mun = municipalities.Municipality(
            **mun_create.model_dump(exclude={"geom"}),
            geom=wkbelement,
        )
        db_records.append(db_mun)
        session.add(db_mun)
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        for db_record in db_records:
            session.refresh(db_record)
        return db_records


def delete_all_municipalities(session: sqlmodel.Session) -> None:
    """Delete all municipalities."""
    for db_municipality in collect_all_municipalities(session):
        session.delete(db_municipality)
    session.commit()


def list_coverage_identifiers(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    name_filter: list[str] | None = None,
    configuration_parameter_values_filter: Optional[
        list[coverages.ConfigurationParameterValue]
    ] = None,
    climatic_indicator_filter: Optional[climaticindicators.ClimaticIndicator] = None,
) -> tuple[list[coverages.CoverageInternal], Optional[int]]:
    all_covs = collect_all_coverages(
        session, configuration_parameter_values_filter, climatic_indicator_filter
    )
    if name_filter is not None:
        for fragment in name_filter:
            all_covs = [c for c in all_covs if fragment.lower() in c.identifier.lower()]
    return (
        all_covs[offset : (offset + limit)],
        len(all_covs) if include_total else None,
    )


def collect_all_coverages(
    session: sqlmodel.Session,
    configuration_parameter_values_filter: Optional[
        list[coverages.ConfigurationParameterValue]
    ] = None,
    climatic_indicator_filter: Optional[climaticindicators.ClimaticIndicator] = None,
) -> list[coverages.CoverageInternal]:
    cov_confs = collect_all_coverage_configurations(
        session,
        configuration_parameter_values_filter=configuration_parameter_values_filter,
        climatic_indicator_filter=climatic_indicator_filter,
    )
    cov_ids = []
    for cov_conf in cov_confs:
        allowed_identifiers = generate_coverage_identifiers(
            cov_conf, configuration_parameter_values_filter
        )
        for cov_id in allowed_identifiers:
            cov_ids.append(
                coverages.CoverageInternal(configuration=cov_conf, identifier=cov_id)
            )
    return cov_ids


def ensure_uncertainty_type_configuration_parameters_exist(
    session: sqlmodel.Session,
) -> tuple[
    coverages.ConfigurationParameterValue, coverages.ConfigurationParameterValue
]:
    """Ensure that the `uncertainty_type` configuration parameter exists.

    Because internally we make use of the `uncertainty_type` configuration parameter,
    we must ensure it and its respective values exist. This can happen if an admin
    user deletes them by accident.
    """
    param_name = base.CoreConfParamName.UNCERTAINTY_TYPE.value
    lower_bound_name = "lower_bound"
    upper_bound_name = "upper_bound"
    param = get_configuration_parameter_by_name(session, param_name)
    if param is None:
        create_configuration_parameter(
            session,
            coverages.ConfigurationParameterCreate(
                name=param_name,
                allowed_values=[
                    coverages.ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                        name=lower_bound_name,
                    ),
                    coverages.ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                        name=upper_bound_name,
                    ),
                ],
            ),
        )
        lower_bound_value = get_configuration_parameter_value_by_names(
            session, param_name, lower_bound_name
        )
        upper_bound_value = get_configuration_parameter_value_by_names(
            session, param_name, upper_bound_name
        )
    else:
        lower_bound_value = get_configuration_parameter_value_by_names(
            session, param_name, lower_bound_name
        )
        upper_bound_value = get_configuration_parameter_value_by_names(
            session, param_name, upper_bound_name
        )
        if lower_bound_value is None:
            lower_bound_value = create_configuration_parameter_value(
                session,
                parameter_value=coverages.ConfigurationParameterValueCreate(
                    name="lower_bound",
                    configuration_parameter_id=param.id,
                ),
            )
        if upper_bound_value is None:
            upper_bound_value = create_configuration_parameter_value(
                session,
                parameter_value=coverages.ConfigurationParameterValueCreate(
                    name="upper_bound",
                    configuration_parameter_id=param.id,
                ),
            )
    return lower_bound_value, upper_bound_value


def get_climatic_indicator(
    session: sqlmodel.Session, climatic_indicator_id: int
) -> Optional[climaticindicators.ClimaticIndicator]:
    return session.get(climaticindicators.ClimaticIndicator, climatic_indicator_id)


def get_climatic_indicator_by_identifier(
    session: sqlmodel.Session, climatic_indicator_identifier: str
) -> Optional[climaticindicators.ClimaticIndicator]:
    name, raw_measure, raw_aggregation_period = climatic_indicator_identifier.split("-")
    try:
        measure_type = static.MeasureType(raw_measure)
        aggregation_period = static.AggregationPeriod(raw_aggregation_period)
    except ValueError as err:
        raise exceptions.InvalidClimaticIndicatorIdentifierError(
            f"Invalid measure type ({raw_measure!r}) or "
            f"aggregation period ({raw_aggregation_period!r})"
        ) from err
    else:
        statement = sqlmodel.select(climaticindicators.ClimaticIndicator).where(
            climaticindicators.ClimaticIndicator.name == name,
            climaticindicators.ClimaticIndicator.measure_type == measure_type,
            climaticindicators.ClimaticIndicator.aggregation_period
            == aggregation_period,
        )
        return session.exec(statement).first()


def list_climatic_indicators(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    name_filter: str | None = None,
    measure_type_filter: str | None = None,
    aggregation_period_filter: str | None = None,
) -> tuple[Sequence[climaticindicators.ClimaticIndicator], Optional[int]]:
    """List existing climatic indicators."""
    statement = sqlmodel.select(climaticindicators.ClimaticIndicator).order_by(
        climaticindicators.ClimaticIndicator.sort_order,
        climaticindicators.ClimaticIndicator.name,
        climaticindicators.ClimaticIndicator.aggregation_period,
        climaticindicators.ClimaticIndicator.measure_type,
    )
    if name_filter is not None:
        statement = _add_substring_filter(
            statement, name_filter, climaticindicators.ClimaticIndicator.name
        )
    if measure_type_filter is not None:
        statement = _add_substring_filter(
            statement,
            measure_type_filter,
            climaticindicators.ClimaticIndicator.measure_type,
        )
    if aggregation_period_filter is not None:
        statement = _add_substring_filter(
            statement,
            aggregation_period_filter,
            climaticindicators.ClimaticIndicator.aggregation_period,
        )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = _get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_climatic_indicators(
    session: sqlmodel.Session,
    name_filter: Optional[str] = None,
    measure_type_filter: str | None = None,
    aggregation_period_filter: str | None = None,
) -> Sequence[climaticindicators.ClimaticIndicator]:
    _, num_total = list_climatic_indicators(
        session,
        limit=1,
        include_total=True,
        name_filter=name_filter,
        measure_type_filter=measure_type_filter,
        aggregation_period_filter=aggregation_period_filter,
    )
    result, _ = list_climatic_indicators(
        session,
        limit=num_total,
        include_total=False,
        name_filter=name_filter,
        measure_type_filter=measure_type_filter,
        aggregation_period_filter=aggregation_period_filter,
    )
    return result


def create_climatic_indicator(
    session: sqlmodel.Session,
    climatic_indicator_create: climaticindicators.ClimaticIndicatorCreate,
) -> climaticindicators.ClimaticIndicator:
    """Create a new climatic indicator."""
    to_refresh = []
    db_climatic_indicator = climaticindicators.ClimaticIndicator(
        **climatic_indicator_create.model_dump(
            exclude={
                "observation_names",
                "forecast_models",
            }
        ),
    )
    to_refresh.append(db_climatic_indicator)
    for obs_name in climatic_indicator_create.observation_names:
        db_obs_name = observations.ClimaticIndicatorObservationName(
            station_manager=obs_name.observation_station_manager,
            indicator_observation_name=obs_name.indicator_observation_name,
        )
        db_climatic_indicator.observation_names.append(db_obs_name)
        to_refresh.append(db_obs_name)
    for forecast_model_info in climatic_indicator_create.forecast_models:
        db_forecast_model_climatic_indicator_link = coverages.ForecastModelClimaticIndicatorLink(
            forecast_model_id=forecast_model_info.forecast_model_id,
            thredds_url_base_path=forecast_model_info.thredds_url_base_path,
            thredds_url_uncertainties_base_path=forecast_model_info.thredds_url_uncertainties_base_path,
        )
        db_climatic_indicator.forecast_model_links.append(
            db_forecast_model_climatic_indicator_link
        )
        to_refresh.append(db_forecast_model_climatic_indicator_link)
    session.add(db_climatic_indicator)
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        for item in to_refresh:
            session.refresh(item)
        return db_climatic_indicator


def update_climatic_indicator(
    session: sqlmodel.Session,
    db_climatic_indicator: climaticindicators.ClimaticIndicator,
    climatic_indicator_update: climaticindicators.ClimaticIndicatorUpdate,
) -> climaticindicators.ClimaticIndicator:
    """Update a climatic indicator."""
    to_refresh = []
    requested_obs_names = {
        "-".join(
            (str(db_climatic_indicator.id), ron.observation_station_manager.value)
        ): ron
        for ron in climatic_indicator_update.observation_names
    }
    existing_obs_names = {
        "-".join((str(db_climatic_indicator.id), ron.station_manager.value)): ron
        for ron in db_climatic_indicator.observation_names
    }
    for existing_key, existing_obs_name in existing_obs_names.items():
        has_been_requested_to_remove = existing_key not in requested_obs_names
        if has_been_requested_to_remove:
            session.delete(existing_obs_name)
    for requested_key, requested_obs_name in requested_obs_names.items():
        if requested_key not in existing_obs_names:  # need to create this one
            db_observation_name = observations.ClimaticIndicatorObservationName(
                station_manager=requested_obs_name.observation_station_manager,
                indicator_observation_name=requested_obs_name.indicator_observation_name,
            )
            db_climatic_indicator.observation_names.append(db_observation_name)
        else:  # already exists, just update
            existing_db_observation_name = existing_obs_names[requested_key]
            existing_db_observation_name.indicator_observation_name = (
                requested_obs_name.indicator_observation_name
            )
            session.add(existing_db_observation_name)
            to_refresh.append(existing_db_observation_name)
    requested_forecast_model_links = {
        fm.forecast_model_id: fm for fm in climatic_indicator_update.forecast_models
    }
    existing_forecast_model_links = {
        db_fm.forecast_model_id: db_fm
        for db_fm in db_climatic_indicator.forecast_model_links
    }
    for existing_fm_id, existing_fm_link in existing_forecast_model_links.items():
        has_been_requested_to_remove = (
            existing_fm_id not in requested_forecast_model_links
        )
        if has_been_requested_to_remove:
            session.delete(existing_fm_link)
    for requested_fm_id, requested_fm in requested_forecast_model_links:
        if (
            requested_fm_id not in existing_forecast_model_links
        ):  # need to create this one
            db_fm_link = coverages.ForecastModelClimaticIndicatorLink(
                forecast_model_id=requested_fm_id,
                climatic_indicator_id=db_climatic_indicator.id,
                thredds_url_base_path=requested_fm.thredds_url_base_path,
                thredds_url_uncertainties_base_path=requested_fm.thredds_url_uncertainties_base_path,
            )
            db_climatic_indicator.forecast_model_links.append(db_fm_link)
        else:  # already exists, just update
            existing_fm_link = existing_forecast_model_links[requested_fm_id]
            existing_fm_link.thredds_url_base_path = requested_fm.thredds_url_base_path
            session.add(existing_fm_link)
            to_refresh.append(existing_fm_link)
    data_ = climatic_indicator_update.model_dump(
        exclude_unset=True,
        exclude={
            "observation_names",
            "forecast_models",
        },
    )
    for key, value in data_.items():
        setattr(db_climatic_indicator, key, value)
    session.add(db_climatic_indicator)
    to_refresh.append(db_climatic_indicator)
    session.commit()
    for item in to_refresh:
        session.refresh(item)
    return db_climatic_indicator


def delete_climatic_indicator(
    session: sqlmodel.Session, climatic_indicator_id: int
) -> None:
    """Delete a climatic indicator."""
    db_indicator = get_climatic_indicator(session, climatic_indicator_id)
    if db_indicator is not None:
        session.delete(db_indicator)
        session.commit()
    else:
        raise exceptions.InvalidClimaticIndicatorIdError()


def _get_total_num_records(session: sqlmodel.Session, statement):
    return session.exec(
        sqlmodel.select(sqlmodel.func.count()).select_from(statement)
    ).first()


def _add_substring_filter(statement, value: str, *columns):
    filter_ = value.replace("%", "")
    filter_ = f"%{filter_}%"
    if len(columns) == 1:
        result = statement.where(columns[0].ilike(filter_))  # type: ignore[attr-defined]
    elif len(columns) > 1:
        result = statement.where(sqlalchemy.or_(*[c.ilike(filter_) for c in columns]))
    else:
        raise RuntimeError("Invalid columns argument")
    return result


def _slugify_internal_value(value: str) -> str:
    """Replace characters in input string in to make it usable as a name."""
    to_translate = "-\, '"
    return value.translate(value.maketrans(to_translate, "_" * len(to_translate)))


def _replace_conf_param_filters_with_climatic_indicator(
    session: sqlmodel.Session,
    possible_values: list[coverages.ConfigurationParameterValue],
) -> tuple[
    list[coverages.ConfigurationParameterValue],
    Optional[climaticindicators.ClimaticIndicator],
]:
    """Tries to extract a `ClimaticIndicator` instance from the input list.

    This function is intended only for compatibility purposes.
    """
    raw_name = None
    raw_measure_type = None
    raw_aggregation_period = None
    new_possible_values = []
    for possible in possible_values:
        param_name = possible.configuration_parameter.name
        logger.debug(f"{param_name=}")
        if param_name == "climatological_variable":
            raw_name = possible.name
        elif param_name == "measure":
            raw_measure_type = possible.name
        elif param_name == "aggregation_period":
            raw_aggregation_period = {"30yr": "thirty_year"}.get(
                possible.name, possible.name
            )
        else:
            new_possible_values.append(possible)
    result = (possible_values, None)
    if all((raw_name, raw_measure_type, raw_aggregation_period)):
        climatic_indicator = get_climatic_indicator_by_identifier(
            session, f"{raw_name}-{raw_measure_type}-{raw_aggregation_period}"
        )
        if climatic_indicator is not None:
            result = (new_possible_values, climatic_indicator)
    return result


def get_observation_station(
    session: sqlmodel.Session, observation_station_id: int
) -> Optional[observations.ObservationStation]:
    return session.get(observations.ObservationStation, observation_station_id)


def get_observation_station_by_code(
    session: sqlmodel.Session, code: str
) -> Optional[observations.ObservationStation]:
    """Get an observation station by its code"""
    return session.exec(
        sqlmodel.select(observations.ObservationStation).where(
            observations.ObservationStation.code == code,
        )
    ).first()


def list_observation_stations(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    name_filter: Optional[str] = None,
    polygon_intersection_filter: Optional[shapely.Polygon] = None,
    manager_filter: Optional[static.ObservationStationManager] = None,
    climatic_indicator_id_filter: Optional[int] = None,
) -> tuple[Sequence[observations.ObservationStation], Optional[int]]:
    """List existing observation stations.

    The ``polygon_intersection_filter`` parameter is expected to be a polygon
    geometry in the EPSG:4326 CRS.
    """
    statement = sqlmodel.select(observations.ObservationStation).order_by(
        observations.ObservationStation.code
    )
    if name_filter is not None:
        statement = _add_substring_filter(
            statement, name_filter, observations.ObservationStation.name
        )
    if polygon_intersection_filter is not None:
        statement = statement.where(
            func.ST_Intersects(
                observations.ObservationStation.geom,
                func.ST_GeomFromWKB(
                    shapely.io.to_wkb(polygon_intersection_filter), 4326
                ),
            )
        )
    if manager_filter is not None:
        statement = statement.where(
            observations.ObservationStation.managed_by == manager_filter
        )
    if climatic_indicator_id_filter is not None:
        statement = statement.join(
            observations.ObservationStationClimaticIndicatorLink,
            observations.ObservationStation.id
            == observations.ObservationStationClimaticIndicatorLink.observation_station_id,
        ).where(
            observations.ObservationStationClimaticIndicatorLink.climatic_indicator_id
            == climatic_indicator_id_filter,
        )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = _get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_observation_stations(
    session: sqlmodel.Session,
    polygon_intersection_filter: Optional[shapely.Polygon] = None,
    manager_filter: Optional[static.ObservationStationManager] = None,
    climatic_indicator_id_filter: Optional[int] = None,
) -> Sequence[observations.ObservationStation]:
    """Collect all observation stations.

    The ``polygon_intersection_filter`` parameter is expected to be a polygon
    geometry in the EPSG:4326 CRS.
    """
    _, num_total = list_observation_stations(
        session,
        limit=1,
        include_total=True,
        polygon_intersection_filter=polygon_intersection_filter,
        manager_filter=manager_filter,
        climatic_indicator_id_filter=climatic_indicator_id_filter,
    )
    result, _ = list_observation_stations(
        session,
        limit=num_total,
        include_total=False,
        polygon_intersection_filter=polygon_intersection_filter,
        manager_filter=manager_filter,
        climatic_indicator_id_filter=climatic_indicator_id_filter,
    )
    return result


def create_observation_station(
    session: sqlmodel.Session,
    observation_station_create: observations.ObservationStationCreate,
) -> observations.ObservationStation:
    """Create a new observation station."""
    geom = shapely.io.from_geojson(observation_station_create.geom.model_dump_json())
    wkbelement = from_shape(geom)
    db_item = observations.ObservationStation(
        **observation_station_create.model_dump(
            exclude={
                "geom",
                "climatic_indicators",
            }
        ),
        geom=wkbelement,
    )
    session.add(db_item)
    for climatic_indicator_id in observation_station_create.climatic_indicators or []:
        climatic_indicator = get_climatic_indicator(session, climatic_indicator_id)
        if climatic_indicator is not None:
            db_item.climatic_indicators.append(climatic_indicator)
        else:
            logger.warning(
                f"climatic indicator {climatic_indicator_id} not found, ignoring..."
            )
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        session.refresh(db_item)
        return db_item


def create_many_observation_stations(
    session: sqlmodel.Session,
    stations_to_create: Sequence[observations.ObservationStationCreate],
) -> list[observations.ObservationStation]:
    """Create several observation stations."""
    db_records = []
    for item_create in stations_to_create:
        geom = shapely.io.from_geojson(item_create.geom.model_dump_json())
        wkbelement = from_shape(geom)
        db_item = observations.ObservationStation(
            **item_create.model_dump(
                exclude={
                    "geom",
                    "climatic_indicators",
                }
            ),
            geom=wkbelement,
        )
        db_records.append(db_item)
        session.add(db_item)
        for climatic_indicator_id in item_create.climatic_indicators or []:
            climatic_indicator = get_climatic_indicator(session, climatic_indicator_id)
            if climatic_indicator is not None:
                db_item.climatic_indicators.append(climatic_indicator)
            else:
                logger.warning(
                    f"climatic indicator {climatic_indicator_id} not found, ignoring..."
                )
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        for db_record in db_records:
            session.refresh(db_record)
        return db_records


def update_observation_station(
    session: sqlmodel.Session,
    db_observation_station: observations.ObservationStation,
    observation_station_update: observations.ObservationStationUpdate,
) -> observations.ObservationStation:
    """Update an observation station."""
    if observation_station_update.geom is not None:
        geom = from_shape(
            shapely.io.from_geojson(observation_station_update.geom.model_dump_json())
        )
    else:
        geom = None
    other_data = observation_station_update.model_dump(
        exclude={
            "geom",
            "climatic_indicators",
        },
        exclude_unset=True,
    )
    data = {**other_data}
    if geom is not None:
        data["geom"] = geom
    for key, value in data.items():
        setattr(db_observation_station, key, value)
    session.add(db_observation_station)
    updated_climatic_indicators = []
    for climatic_indicator_id in observation_station_update.climatic_indicators or []:
        climatic_indicator = get_climatic_indicator(session, climatic_indicator_id)
        if climatic_indicator is not None:
            updated_climatic_indicators.append(climatic_indicator)
        else:
            logger.warning(
                f"Climatic indicator with id {climatic_indicator_id} not found, "
                f"ignoring..."
            )
    db_observation_station.climatic_indicators = updated_climatic_indicators
    session.commit()
    session.refresh(db_observation_station)
    return db_observation_station


def delete_observation_station(
    session: sqlmodel.Session, observation_station_id: int
) -> None:
    """Delete an observation station."""
    db_item = get_observation_station(session, observation_station_id)
    if db_item is not None:
        session.delete(db_item)
        session.commit()
    else:
        raise RuntimeError("Observation station not found")


def get_observation_measurement(
    session: sqlmodel.Session, observation_measurement_id: int
) -> Optional[observations.ObservationMeasurement]:
    return session.get(observations.ObservationMeasurement, observation_measurement_id)


def list_observation_measurements(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    observation_station_id_filter: Optional[int] = None,
    climatic_indicator_id_filter: Optional[int] = None,
    aggregation_type_filter: Optional[static.MeasurementAggregationType] = None,
    include_total: bool = False,
) -> tuple[Sequence[observations.ObservationMeasurement], Optional[int]]:
    """List existing observation measurements."""
    statement = sqlmodel.select(observations.ObservationMeasurement).order_by(
        observations.ObservationMeasurement.date
    )
    if observation_station_id_filter is not None:
        statement = statement.where(
            observations.ObservationMeasurement.observation_station_id
            == observation_station_id_filter
        )
    if climatic_indicator_id_filter is not None:
        statement = statement.where(
            observations.ObservationMeasurement.climatic_indicator_id
            == climatic_indicator_id_filter
        )
    if aggregation_type_filter is not None:
        statement = statement.where(
            observations.ObservationMeasurement.measurement_aggregation_type
            == aggregation_type_filter.name
        )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = _get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_observation_measurements(
    session: sqlmodel.Session,
    *,
    observation_station_id_filter: Optional[int] = None,
    climatic_indicator_id_filter: Optional[int] = None,
    aggregation_type_filter: Optional[static.MeasurementAggregationType] = None,
) -> Sequence[observations.ObservationMeasurement]:
    _, num_total = list_observation_measurements(
        session,
        limit=1,
        observation_station_id_filter=observation_station_id_filter,
        climatic_indicator_id_filter=climatic_indicator_id_filter,
        aggregation_type_filter=aggregation_type_filter,
        include_total=True,
    )
    result, _ = list_observation_measurements(
        session,
        limit=num_total,
        observation_station_id_filter=observation_station_id_filter,
        climatic_indicator_id_filter=climatic_indicator_id_filter,
        aggregation_type_filter=aggregation_type_filter,
        include_total=False,
    )
    return result


def create_observation_measurement(
    session: sqlmodel.Session,
    observation_measurement_create: observations.ObservationMeasurementUpdate,
) -> observations.ObservationMeasurement:
    """Create a new observation measurement."""
    db_measurement = observations.ObservationMeasurement(
        **observation_measurement_create.model_dump()
    )
    session.add(db_measurement)
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        session.refresh(db_measurement)
        return db_measurement


def create_many_observation_measurements(
    session: sqlmodel.Session,
    observation_measurements_to_create: Sequence[
        observations.ObservationMeasurementCreate
    ],
) -> list[observations.ObservationMeasurement]:
    """Create several observation measurements."""
    db_records = []
    for measurement_create in observation_measurements_to_create:
        db_measurement = observations.ObservationMeasurement(
            observation_station_id=measurement_create.observation_station_id,
            climatic_indicator_id=measurement_create.climatic_indicator_id,
            value=measurement_create.value,
            date=measurement_create.date,
            measurement_aggregation_type=measurement_create.measurement_aggregation_type,
        )
        db_records.append(db_measurement)
        session.add(db_measurement)
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        for db_record in db_records:
            session.refresh(db_record)
        return db_records


def delete_observation_measurement(
    session: sqlmodel.Session, observation_measurement_id: int
) -> None:
    """Delete an observation measurement."""
    if (
        db_measurement := get_observation_measurement(
            session, observation_measurement_id
        )
    ) is not None:
        session.delete(db_measurement)
        session.commit()
    else:
        raise RuntimeError("Observation measurement not found")


def get_observation_series_configuration(
    session: sqlmodel.Session, observation_series_configuration_id: int
) -> Optional[observations.ObservationSeriesConfiguration]:
    return session.get(
        observations.ObservationSeriesConfiguration, observation_series_configuration_id
    )


def get_observation_series_configuration_by_identifier(
    session: sqlmodel.Session, identifier: str
) -> Optional[observations.ObservationSeriesConfiguration]:
    parts = identifier.split("-")
    climatic_indicator_identifier = "-".join(parts[:3])
    climatic_indicator = get_climatic_indicator_by_identifier(
        session, climatic_indicator_identifier
    )
    if climatic_indicator is None:
        raise exceptions.InvalidObservationSeriesConfigurationIdentifierError(
            f"climatic indicator {climatic_indicator_identifier} does not exist"
        )
    raw_station_managers, raw_measurement_aggregation = parts[3:5]
    managers = [
        static.ObservationStationManager(m) for m in raw_station_managers.split(":")
    ]
    measurement_aggregation_type = static.MeasurementAggregationType(
        raw_measurement_aggregation
    )
    statement = sqlmodel.select(observations.ObservationSeriesConfiguration).where(
        observations.ObservationSeriesConfiguration.climatic_indicator_id
        == climatic_indicator.id,
        observations.ObservationSeriesConfiguration.measurement_aggregation_type
        == measurement_aggregation_type,
        observations.ObservationSeriesConfiguration.station_managers == managers,
    )
    return session.exec(statement).first()


def list_observation_series_configurations(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
) -> tuple[Sequence[observations.ObservationSeriesConfiguration], Optional[int]]:
    """List existing observation series configurations."""
    statement = sqlmodel.select(observations.ObservationSeriesConfiguration).order_by(
        observations.ObservationSeriesConfiguration.id
    )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = _get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_observation_series_configurations(
    session: sqlmodel.Session,
) -> Sequence[observations.ObservationSeriesConfiguration]:
    """Collect all observation series configurations."""
    _, num_total = list_observation_series_configurations(
        session,
        limit=1,
        include_total=True,
    )
    result, _ = list_observation_series_configurations(
        session,
        limit=num_total,
        include_total=False,
    )
    return result


def create_observation_series_configuration(
    session: sqlmodel.Session,
    observation_series_configuration_create: observations.ObservationSeriesConfigurationCreate,
) -> observations.ObservationSeriesConfiguration:
    """Create a new observation series configuration."""
    db_series_conf = observations.ObservationSeriesConfiguration(
        **observation_series_configuration_create.model_dump(),
    )
    session.add(db_series_conf)
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        session.refresh(db_series_conf)
        return db_series_conf


def update_observation_series_configuration(
    session: sqlmodel.Session,
    db_observation_series_configuration: observations.ObservationSeriesConfiguration,
    observation_series_configuration_update: observations.ObservationSeriesConfigurationUpdate,
) -> observations.ObservationSeriesConfiguration:
    """Update an observation series configuration."""
    data = observation_series_configuration_update.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_observation_series_configuration, key, value)
    session.add(db_observation_series_configuration)
    session.commit()
    session.refresh(db_observation_series_configuration)
    return db_observation_series_configuration


def delete_observation_series_configuration(
    session: sqlmodel.Session, observation_series_configuration_id: int
) -> None:
    """Delete an observation series configuration."""
    db_item = get_observation_station(session, observation_series_configuration_id)
    if db_item is not None:
        session.delete(db_item)
        session.commit()
    else:
        raise RuntimeError("Observation series configuration not found")


def list_spatial_regions(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
) -> tuple[Sequence[base.SpatialRegion], Optional[int]]:
    statement = sqlmodel.select(base.SpatialRegion).order_by(base.SpatialRegion.name)
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = _get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_spatial_regions(
    session: sqlmodel.Session,
) -> Sequence[base.SpatialRegion]:
    _, num_total = list_spatial_regions(
        session,
        limit=1,
        include_total=True,
    )
    result, _ = list_spatial_regions(
        session,
        limit=num_total,
        include_total=False,
    )
    return result


def get_spatial_region(
    session: sqlmodel.Session, spatial_region_id: int
) -> Optional[base.SpatialRegion]:
    return session.get(base.SpatialRegion, spatial_region_id)


def get_spatial_region_by_name(
    session: sqlmodel.Session, name: str
) -> Optional[base.SpatialRegion]:
    """Get a spatial region by its name."""
    return session.exec(
        sqlmodel.select(base.SpatialRegion).where(base.SpatialRegion.name == name)
    ).first()


def create_spatial_region(
    session: sqlmodel.Session,
    spatial_region_create: base.SpatialRegionCreate,
):
    """Create a new spatial region."""
    geom = shapely.io.from_geojson(spatial_region_create.geom.model_dump_json())
    wkbelement = from_shape(geom)
    db_item = base.SpatialRegion(
        **spatial_region_create.model_dump(exclude={"geom"}),
        geom=wkbelement,
    )
    session.add(db_item)
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        session.refresh(db_item)
        return db_item


def update_spatial_region(
    session: sqlmodel.Session,
    db_spatial_region: base.SpatialRegion,
    spatial_region_update: base.SpatialRegionUpdate,
) -> base.SpatialRegion:
    """Update a spatial region."""
    geom = from_shape(
        shapely.io.from_geojson(spatial_region_update.geom.model_dump_json())
    )
    other_data = spatial_region_update.model_dump(exclude={"geom"}, exclude_unset=True)
    data = {**other_data, "geom": geom}
    for key, value in data.items():
        setattr(db_spatial_region, key, value)
    session.add(db_spatial_region)
    session.commit()
    session.refresh(db_spatial_region)
    return db_spatial_region


def delete_spatial_region(session: sqlmodel.Session, spatial_region_id: int) -> None:
    """Delete a spatial region."""
    db_item = get_spatial_region(session, spatial_region_id)
    if db_item is not None:
        session.delete(db_item)
        session.commit()
    else:
        raise RuntimeError("Spatial region not found")


def list_forecast_coverage_configurations(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    climatic_indicator_name_filter: Optional[str] = None,
    climatic_indicator_filter: Optional[climaticindicators.ClimaticIndicator] = None,
) -> tuple[Sequence[coverages.ForecastCoverageConfiguration], Optional[int]]:
    """List existing forecast coverage configurations."""
    statement = sqlmodel.select(coverages.ForecastCoverageConfiguration).order_by(
        coverages.ForecastCoverageConfiguration.id
    )
    if climatic_indicator_filter is not None:
        statement = statement.where(
            coverages.ForecastCoverageConfiguration.climatic_indicator_id
            == climatic_indicator_filter.id
        )
    if climatic_indicator_name_filter is not None:
        filter_ = climatic_indicator_name_filter.replace("%", "")
        filter_ = f"%{filter_}%"
        statement = statement.join(
            climaticindicators.ClimaticIndicator,
            climaticindicators.ClimaticIndicator.id
            == coverages.ForecastCoverageConfiguration.climatic_indicator_id,
        ).where(climaticindicators.ClimaticIndicator.name.ilike(filter_))
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = _get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_forecast_coverage_configurations(
    session: sqlmodel.Session,
    climatic_indicator_name_filter: Optional[str] = None,
    climatic_indicator_filter: Optional[climaticindicators.ClimaticIndicator] = None,
) -> Sequence[coverages.ForecastCoverageConfiguration]:
    _, num_total = list_forecast_coverage_configurations(
        session,
        limit=1,
        include_total=True,
        climatic_indicator_name_filter=climatic_indicator_name_filter,
        climatic_indicator_filter=climatic_indicator_filter,
    )
    result, _ = list_forecast_coverage_configurations(
        session,
        limit=num_total,
        include_total=False,
        climatic_indicator_name_filter=climatic_indicator_name_filter,
        climatic_indicator_filter=climatic_indicator_filter,
    )
    return result


def collect_all_forecast_coverage_configurations_with_identifier_filter(
    session: sqlmodel.Session,
    identifier_filter: Optional[str] = None,
) -> list[coverages.ForecastCoverageConfiguration]:
    all_fccs = collect_all_forecast_coverage_configurations(session)
    if identifier_filter is not None:
        result = [fcc for fcc in all_fccs if identifier_filter in fcc.identifier]
    else:
        result = all_fccs
    return result


def get_forecast_coverage_configuration(
    session: sqlmodel.Session,
    forecast_coverage_configuration_id: int,
) -> Optional[coverages.ForecastCoverageConfiguration]:
    return session.get(
        coverages.ForecastCoverageConfiguration, forecast_coverage_configuration_id
    )


def _get_five_part_fcc(
    session: sqlmodel.Session,
    climatic_indicator: climaticindicators.ClimaticIndicator,
    spatial_region: base.SpatialRegion,
) -> Optional[coverages.ForecastCoverageConfiguration]:
    statement = sqlmodel.select(coverages.ForecastCoverageConfiguration).where(
        coverages.ForecastCoverageConfiguration.climatic_indicator_id
        == climatic_indicator.id,
        coverages.ForecastCoverageConfiguration.spatial_region_id == spatial_region.id,
    )
    query_result = session.exec(statement).all()
    # choose the item that has more than one forecast model and more than one
    # year period
    result = None
    for fcc in query_result:
        fcc: coverages.ForecastCoverageConfiguration
        if len(fcc.forecast_model_links) > 1 and len(fcc.year_periods) > 1:
            result = fcc
            break

    # # choose the shorter identifier of those forecast coverage configurations
    # # found in the DB
    # result = None
    # for fcc in query_result:
    #     fcc: coverages.ForecastCoverageConfiguration
    #     if result is None:
    #         result = fcc
    #     else:
    #         result = result if len(result.identifier) < len(fcc.identifier) else fcc
    return result


def _get_six_part_fcc(
    session: sqlmodel.Session,
    climatic_indicator: climaticindicators.ClimaticIndicator,
    spatial_region: base.SpatialRegion,
    sixth_part: str,
) -> Optional[coverages.ForecastCoverageConfiguration]:
    """Try to find a forecast coverage identifier made up of six parts.

    The sixth part can either represent a forecast model or a year period. In this
    function we start by checking whether thhe sixth partt is a forecast model and
    then we check if it is a year period.
    """
    statement = sqlmodel.select(coverages.ForecastCoverageConfiguration).where(
        coverages.ForecastCoverageConfiguration.climatic_indicator_id
        == climatic_indicator.id,
        coverages.ForecastCoverageConfiguration.spatial_region_id == spatial_region.id,
    )
    forecast_model_name = sixth_part
    forecast_model = get_forecast_model_by_name(session, forecast_model_name)
    result = None
    if forecast_model is not None:
        statement = statement.join(
            coverages.ForecastCoverageConfigurationForecastModelLink,
            (
                coverages.ForecastCoverageConfiguration.id
                == coverages.ForecastCoverageConfigurationForecastModelLink.forecast_coverage_configuration_id
            ),
        ).where(
            coverages.ForecastCoverageConfigurationForecastModelLink.forecast_model_id
            == forecast_model.id
        )
        query_result: Sequence[coverages.ForecastCoverageConfiguration] = session.exec(
            statement
        ).all()
        for fcc in query_result:
            if len(fcc.forecast_model_links) == 1 and len(fcc.year_periods) > 1:
                result = fcc
                break
    else:
        year_period_value = sixth_part
        try:
            year_period = static.ForecastYearPeriod(year_period_value)
        except ValueError:
            raise exceptions.InvalidForecastYearPeriodError(
                f"{year_period_value!r} is not a valid forecast year period"
            )
        else:
            statement = statement.where(
                year_period.name
                == sqlalchemy.any_(coverages.ForecastCoverageConfiguration.year_periods)
            )
            query_result: Sequence[
                coverages.ForecastCoverageConfiguration
            ] = session.exec(statement).all()
            for fcc in query_result:
                if len(fcc.year_periods) == 1 and len(fcc.forecast_model_links) > 1:
                    result = fcc
                    break
    return result


def _get_seven_part_fcc(
    session: sqlmodel.Session,
    climatic_indicator: climaticindicators.ClimaticIndicator,
    spatial_region: base.SpatialRegion,
    sixth_part: str,
    seventh_part: str,
) -> Optional[coverages.ForecastCoverageConfiguration]:
    """Try to find a forecast coverage identifier made up of seven parts.

    The sixth and seventh parts will be the forecast model and the year period,
    respectively.
    """
    statement = sqlmodel.select(coverages.ForecastCoverageConfiguration).where(
        coverages.ForecastCoverageConfiguration.climatic_indicator_id
        == climatic_indicator.id,  # noqa
        coverages.ForecastCoverageConfiguration.spatial_region_id == spatial_region.id,  # noqa
    )
    forecast_model_name = sixth_part
    forecast_model = get_forecast_model_by_name(session, forecast_model_name)
    if forecast_model is None:
        raise exceptions.InvalidForecastCoverageConfigurationIdentifierError(
            f"{forecast_model_name!r} is not a valid forecast model"
        )
    year_period_value = seventh_part
    try:
        year_period = static.ForecastYearPeriod(year_period_value)
    except ValueError:
        raise exceptions.InvalidForecastYearPeriodError(
            f"{year_period_value!r} is not a valid forecast year period"
        )
    statement = (
        statement.join(
            coverages.ForecastCoverageConfigurationForecastModelLink,
            (
                coverages.ForecastCoverageConfiguration.id
                == coverages.ForecastCoverageConfigurationForecastModelLink.forecast_coverage_configuration_id
            ),
        )
        .where(
            coverages.ForecastCoverageConfigurationForecastModelLink.forecast_model_id
            == forecast_model.id
        )
        .where(
            year_period.name
            == sqlalchemy.any_(coverages.ForecastCoverageConfiguration.year_periods)
        )
    )
    query_result: Sequence[coverages.ForecastCoverageConfiguration] = session.exec(
        statement
    ).all()
    result = None
    for fcc in query_result:
        if len(fcc.forecast_model_links) == 1 and len(fcc.year_periods) == 1:
            result = fcc
            break
    return result


def get_forecast_coverage_configuration_by_identifier(
    session: sqlmodel.Session, identifier: str
) -> Optional[coverages.ForecastCoverageConfiguration]:
    error_message = f"{identifier!r} is not a valid forecast coverage identifier"
    parts = identifier.split("-")
    if parts[0] == "forecast":
        if len(parts) >= 5:
            climatic_indicator_identifier = "-".join(parts[1:4])
            climatic_indicator = get_climatic_indicator_by_identifier(
                session, climatic_indicator_identifier
            )
            if climatic_indicator is None:
                raise exceptions.InvalidClimaticIndicatorIdentifierError(
                    f"{climatic_indicator_identifier!r} is not a valid climatic "
                    f"indicator identifier"
                )
            spatial_region_name = parts[4]
            spatial_region = get_spatial_region_by_name(session, spatial_region_name)
            if spatial_region is None:
                raise exceptions.InvalidSpatialRegionNameError(
                    f"{spatial_region_name!r} is not a valid spatial region name"
                )

            if len(parts) == 5:
                result = _get_five_part_fcc(session, climatic_indicator, spatial_region)
            elif len(parts) == 6:
                result = _get_six_part_fcc(
                    session, climatic_indicator, spatial_region, parts[5]
                )
            elif len(parts) == 7:
                result = _get_seven_part_fcc(
                    session, climatic_indicator, spatial_region, parts[5], parts[6]
                )
            else:
                raise exceptions.InvalidForecastCoverageConfigurationIdentifierError(
                    error_message + "- identifier is too long"
                )
            return result
        else:
            raise exceptions.InvalidForecastCoverageConfigurationIdentifierError(
                error_message + "- identifier is too short"
            )
    else:
        raise exceptions.InvalidForecastCoverageConfigurationIdentifierError(
            error_message
        )

    # if len(parts) >= 5 and parts[0] == "forecast":
    #     climatic_indicator_identifier = "-".join(parts[1:4])
    #     climatic_indicator = get_climatic_indicator_by_identifier(
    #         session, climatic_indicator_identifier
    #     )
    #     if climatic_indicator is None:
    #         raise exceptions.InvalidClimaticIndicatorIdentifierError(
    #             f"{climatic_indicator_identifier!r} is not a valid climatic "
    #             f"indicator identifier"
    #         )
    #     spatial_region_name = parts[4]
    #     spatial_region = get_spatial_region_by_name(session, spatial_region_name)
    #     if spatial_region is None:
    #         raise exceptions.InvalidSpatialRegionNameError(
    #             f"{spatial_region_name!r} is not a valid spatial region name"
    #         )
    #     # forecast coverage configuration identifier can either have just the
    #     # climatic_indicator and spatial_region...
    #     statement = (
    #         sqlmodel.select(coverages.ForecastCoverageConfiguration)
    #         .where(
    #             coverages.ForecastCoverageConfiguration.climatic_indicator_id == climatic_indicator.id,
    #             coverages.ForecastCoverageConfiguration.spatial_region_id == spatial_region.id,
    #         )
    #     )
    #     if len(parts) > 5:
    #         #  ...or it can have an additional part with either the forecast_model
    #         #  or the year_period
    #         forecast_model_name = parts[5]
    #         forecast_model = get_forecast_model_by_name(session, forecast_model_name)
    #         if forecast_model is not None:
    #             statement = statement.join(
    #                 coverages.ForecastCoverageConfigurationForecastModelLink,
    #                 (
    #                     coverages.ForecastCoverageConfiguration.id
    #                     == coverages.ForecastCoverageConfigurationForecastModelLink.forecast_coverage_configuration_id
    #                 ),
    #             ).where(
    #                 coverages.ForecastCoverageConfigurationForecastModelLink.forecast_model_id
    #                 == forecast_model.id
    #             )
    #             query_result: Sequence[
    #                 coverages.ForecastCoverageConfiguration
    #             ] = session.exec(statement).all()
    #             logger.debug(f"{[fcc.identifier for fcc in query_result]=}")
    #             if len(query_result) == 0:
    #                 result = None
    #             elif len(query_result) == 1:
    #                 possible_result: coverages.ForecastCoverageConfiguration = (
    #                     query_result[0])
    #                 result = (
    #                     possible_result
    #                     if possible_result.identifier == identifier else None
    #                 )
    #             else:
    #                 for forecast_cov_conf in query_result:
    #                     logger.debug(f"processing {forecast_cov_conf.identifier!r}...")
    #                     logger.debug(f"{len(forecast_cov_conf.forecast_model_links)=}")
    #                     if len(forecast_cov_conf.forecast_model_links) == 1:
    #                         result = forecast_cov_conf
    #                         break
    #                 else:
    #                     raise exceptions.InvalidForecastCoverageConfigurationIdentifierError(
    #                         f"Could not find a suitable coverage configuration "
    #                         f"identifier with a particular forecast model "
    #                         f"of {forecast_model_name!r}"
    #                     )
    #         else:
    #             year_period_value = parts[5]
    #             try:
    #                 year_period = static.ForecastYearPeriod(year_period_value)
    #             except ValueError:
    #                 raise exceptions.InvalidForecastYearPeriodError(
    #                     f"{year_period_value!r} is not a valid forecast year period"
    #                 )
    #             else:
    #                 statement = statement.where(
    #                     year_period.name
    #                     == sqlalchemy.any_(
    #                         coverages.ForecastCoverageConfiguration.year_periods
    #                     )
    #                 )
    #                 query_result: Sequence[
    #                     coverages.ForecastCoverageConfiguration
    #                 ] = session.exec(statement).all()
    #                 logger.debug(f"{[i.identifier for i in query_result]=}")
    #                 if len(query_result) == 0:
    #                     result = None
    #                 elif len(query_result) == 1:
    #                     possible_result: coverages.ForecastCoverageConfiguration = (
    #                         query_result[0])
    #                     result = (
    #                         possible_result
    #                         if possible_result.identifier == identifier else None
    #                     )
    #                 else:
    #                     for forecast_cov_conf in query_result:
    #                         if len(forecast_cov_conf.year_periods) == 1:
    #                             result = forecast_cov_conf
    #                             break
    #                     else:
    #                         raise exceptions.InvalidForecastCoverageConfigurationIdentifierError(
    #                             f"Could not find a suitable coverage configuration "
    #                             f"identifier with a particular forecast year period "
    #                             f"of {year_period.name!r}"
    #                         )
    #     else:
    #         query_result = session.exec(statement).all()
    #         logger.debug(f"{[fcc.identifier for fcc in query_result]=}")
    #         # choose the shorter identifier of those forecast coverage configurations
    #         # found in the DB
    #         result = None
    #         for fcc in query_result:
    #             fcc: coverages.ForecastCoverageConfiguration
    #             if result is None:
    #                 result = fcc
    #             else:
    #                 result = result if len(result.identifier) < len(fcc.identifier) else fcc
    #     return result
    # else:
    #     raise exceptions.InvalidForecastCoverageConfigurationIdentifierError(
    #         f"{identifier!r} is not a valid forecast coverage configuration "
    #         f"identifier"
    #     )


def create_forecast_coverage_configuration(
    session: sqlmodel.Session,
    forecast_coverage_configuration_create: coverages.ForecastCoverageConfigurationCreate,
) -> coverages.ForecastCoverageConfiguration:
    db_forecast_coverage_configuration = coverages.ForecastCoverageConfiguration(
        **forecast_coverage_configuration_create.model_dump(
            exclude={
                "time_windows",
                "observation_series_configurations",
            }
        )
    )
    session.add(db_forecast_coverage_configuration)
    for forecast_model_id in forecast_coverage_configuration_create.forecast_models:
        db_forecast_model = get_forecast_model(session, forecast_model_id)
        if db_forecast_model is not None:
            db_forecast_coverage_configuration.forecast_model_links.append(
                coverages.ForecastCoverageConfigurationForecastModelLink(
                    forecast_model_id=forecast_model_id,
                )
            )
        else:
            raise ValueError(f"Forecast model {forecast_model_id!r} not found")
    for forecast_time_window_id in (
        forecast_coverage_configuration_create.forecast_time_windows or []
    ):
        db_forecast_time_window = get_forecast_time_window(
            session, forecast_time_window_id
        )
        if db_forecast_time_window is not None:
            db_forecast_coverage_configuration.forecast_time_window_links.append(
                coverages.ForecastCoverageConfigurationForecastTimeWindowLink(
                    forecast_time_window=db_forecast_time_window
                )
            )
        else:
            raise ValueError(
                f"Forecast time window {forecast_time_window_id!r} not found"
            )
    for obs_series_conf_id in (
        forecast_coverage_configuration_create.observation_series_configurations or []
    ):
        db_obs_series_conf = get_observation_series_configuration(
            session, obs_series_conf_id
        )
        if db_obs_series_conf is not None:
            db_forecast_coverage_configuration.observation_series_configuration_links.append(
                coverages.ForecastCoverageConfigurationObservationSeriesConfigurationLink(
                    observation_series_configuration=db_obs_series_conf
                )
            )
        else:
            raise ValueError(
                f"observation series configuration {obs_series_conf_id!r} not found"
            )
    session.commit()
    session.refresh(db_forecast_coverage_configuration)
    return db_forecast_coverage_configuration


def update_forecast_coverage_configuration(
    session: sqlmodel.Session,
    db_forecast_coverage_configuration: coverages.ForecastCoverageConfiguration,
    forecast_coverage_configuration_update: coverages.ForecastCoverageConfigurationUpdate,
) -> coverages.ForecastCoverageConfiguration:
    """Update a forecast coverage configuration."""
    existing_forecast_model_links_to_keep = []
    existing_forecast_model_links_discard = []
    for (
        existing_forecast_model_link
    ) in db_forecast_coverage_configuration.forecast_model_links:
        has_been_requested_to_remove = (
            existing_forecast_model_link.forecast_model_id
            not in [
                fm_id
                for fm_id in forecast_coverage_configuration_update.forecast_models
            ]
        )
        if not has_been_requested_to_remove:
            existing_forecast_model_links_to_keep.append(existing_forecast_model_link)
        else:
            existing_forecast_model_links_discard.append(existing_forecast_model_link)
    db_forecast_coverage_configuration.forecast_model_links = (
        existing_forecast_model_links_to_keep
    )
    for to_discard in existing_forecast_model_links_discard:
        session.delete(to_discard)
    existing_time_window_links_to_keep = []
    existing_time_window_links_discard = []
    for (
        existing_time_window_link
    ) in db_forecast_coverage_configuration.forecast_time_window_links:
        has_been_requested_to_remove = (
            existing_time_window_link.forecast_time_window_id
            not in [
                tw_id
                for tw_id in forecast_coverage_configuration_update.forecast_time_windows
            ]
        )
        if not has_been_requested_to_remove:
            existing_time_window_links_to_keep.append(existing_time_window_link)
        else:
            existing_time_window_links_discard.append(existing_time_window_link)
    db_forecast_coverage_configuration.forecast_time_window_links = (
        existing_time_window_links_to_keep
    )
    for to_discard in existing_time_window_links_discard:
        session.delete(to_discard)
    existing_obs_series_conf_links_to_keep = []
    existing_obs_series_conf_links_discard = []
    for (
        existing_obs_series_conf_link
    ) in db_forecast_coverage_configuration.observation_series_configuration_links:
        has_been_requested_to_remove = (
            existing_obs_series_conf_link.observation_series_configuration_id
            not in [
                osc_id
                for osc_id in forecast_coverage_configuration_update.observation_series_configurations
            ]
        )
        if not has_been_requested_to_remove:
            existing_obs_series_conf_links_to_keep.append(existing_obs_series_conf_link)
        else:
            existing_obs_series_conf_links_discard.append(existing_obs_series_conf_link)
    db_forecast_coverage_configuration.observation_series_configuration_links = (
        existing_obs_series_conf_links_to_keep
    )
    for to_discard in existing_obs_series_conf_links_discard:
        session.delete(to_discard)

    for forecast_model_id in forecast_coverage_configuration_update.forecast_models:
        already_there = forecast_model_id in (
            fml.forecast_model_id
            for fml in db_forecast_coverage_configuration.forecast_model_links
        )
        if not already_there:
            db_forecast_model_link = (
                coverages.ForecastCoverageConfigurationForecastModelLink(
                    forecast_model_id=forecast_model_id,
                )
            )
            db_forecast_coverage_configuration.forecast_model_links.append(
                db_forecast_model_link
            )
    for time_window_id in forecast_coverage_configuration_update.forecast_time_windows:
        already_there = time_window_id in (
            twl.forecast_time_window_id
            for twl in db_forecast_coverage_configuration.forecast_time_window_links
        )
        if not already_there:
            db_time_window_link = (
                coverages.ForecastCoverageConfigurationForecastTimeWindowLink(
                    forecast_time_window_id=time_window_id
                )
            )
            db_forecast_coverage_configuration.forecast_time_window_links.append(
                db_time_window_link
            )
    for (
        obs_series_conf_id
    ) in forecast_coverage_configuration_update.observation_series_configurations:
        already_there = obs_series_conf_id in (
            oscl.observation_series_configuration_id
            for oscl in db_forecast_coverage_configuration.observation_series_configuration_links
        )
        if not already_there:
            db_obs_series_conf_link = coverages.ForecastCoverageConfigurationObservationSeriesConfigurationLink(
                observation_series_configuration_id=obs_series_conf_id
            )
            db_forecast_coverage_configuration.observation_series_configuration_links.append(
                db_obs_series_conf_link
            )
    data_ = forecast_coverage_configuration_update.model_dump(
        exclude={
            "time_windows",
            "observation_series_configurations",
        },
        exclude_unset=True,
        exclude_none=True,
    )
    for key, value in data_.items():
        setattr(db_forecast_coverage_configuration, key, value)
    session.add(db_forecast_coverage_configuration)
    session.commit()
    session.refresh(db_forecast_coverage_configuration)
    return db_forecast_coverage_configuration


def delete_forecast_coverage_configuration(
    session: sqlmodel.Session, forecast_coverage_configuration_id: int
) -> None:
    db_item = get_forecast_coverage_configuration(
        session, forecast_coverage_configuration_id
    )
    if db_item is not None:
        session.delete(db_item)
        session.commit()
    else:
        raise RuntimeError("Forecast coverage configuration not found")


def list_forecast_models(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    name_filter: str | None = None,
    include_total: bool = False,
) -> tuple[Sequence[coverages.ForecastModel], Optional[int]]:
    """List existing forecast models."""
    statement = sqlmodel.select(coverages.ForecastModel).order_by(
        coverages.ForecastModel.sort_order
    )
    if name_filter is not None:
        statement = _add_substring_filter(
            statement, name_filter, coverages.ForecastModel.internal_value
        )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = _get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_forecast_models(
    session: sqlmodel.Session,
    name_filter: str | None = None,
) -> Sequence[coverages.ForecastModel]:
    _, num_total = list_forecast_models(
        session,
        limit=1,
        name_filter=name_filter,
        include_total=True,
    )
    result, _ = list_forecast_models(
        session,
        limit=num_total,
        name_filter=name_filter,
        include_total=False,
    )
    return result


def get_forecast_model(
    session: sqlmodel.Session,
    forecast_model_id: int,
) -> Optional[coverages.ForecastModel]:
    return session.get(coverages.ForecastModel, forecast_model_id)


def get_forecast_model_by_name(
    session: sqlmodel.Session, name: str
) -> Optional[coverages.ForecastModel]:
    """Get a forecast model by its name."""
    return session.exec(
        sqlmodel.select(coverages.ForecastModel).where(
            coverages.ForecastModel.name == name
        )
    ).first()


def create_forecast_model(
    session: sqlmodel.Session,
    forecast_model_create: coverages.ForecastModelCreate,
) -> coverages.ForecastModel:
    """Create a new forecast model."""
    db_forecast_model = coverages.ForecastModel(
        **forecast_model_create.model_dump(),
    )
    session.add(db_forecast_model)
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        session.refresh(db_forecast_model)
    return db_forecast_model


def update_forecast_model(
    session: sqlmodel.Session,
    db_forecast_model: coverages.ForecastModel,
    forecast_model_update: coverages.ForecastModelUpdate,
) -> coverages.ForecastModel:
    """Update a forecast model."""
    for key, value in forecast_model_update.model_dump().items():
        setattr(db_forecast_model, key, value)
    session.add(db_forecast_model)
    session.commit()
    session.refresh(db_forecast_model)
    return db_forecast_model


def delete_forecast_model(session: sqlmodel.Session, forecast_model_id: int) -> None:
    db_item = get_forecast_model(session, forecast_model_id)
    if db_item is not None:
        session.delete(db_item)
        session.commit()
    else:
        raise RuntimeError("Forecast model not found")


def list_forecast_time_windows(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    name_filter: str | None = None,
    include_total: bool = False,
) -> tuple[Sequence[coverages.ForecastTimeWindow], Optional[int]]:
    """List existing forecast time windows."""
    statement = sqlmodel.select(coverages.ForecastTimeWindow).order_by(
        coverages.ForecastTimeWindow.sort_order
    )
    if name_filter is not None:
        statement = _add_substring_filter(
            statement, name_filter, coverages.ForecastModel.internal_value
        )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = _get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_forecast_time_windows(
    session: sqlmodel.Session,
    name_filter: str | None = None,
) -> Sequence[coverages.ForecastTimeWindow]:
    _, num_total = list_forecast_time_windows(
        session,
        limit=1,
        name_filter=name_filter,
        include_total=True,
    )
    result, _ = list_forecast_time_windows(
        session,
        limit=num_total,
        name_filter=name_filter,
        include_total=False,
    )
    return result


def get_forecast_time_window(
    session: sqlmodel.Session,
    forecast_time_window_id: int,
) -> Optional[coverages.ForecastTimeWindow]:
    return session.get(coverages.ForecastTimeWindow, forecast_time_window_id)


def get_forecast_time_window_by_name(
    session: sqlmodel.Session, name: str
) -> Optional[coverages.ForecastTimeWindow]:
    """Get a forecast time window by its name."""
    return session.exec(
        sqlmodel.select(coverages.ForecastTimeWindow).where(
            coverages.ForecastTimeWindow.name == name
        )
    ).first()


def create_forecast_time_window(
    session: sqlmodel.Session,
    forecast_time_window_create: coverages.ForecastTimeWindowCreate,
) -> coverages.ForecastTimeWindow:
    """Create a new forecast time window."""
    db_tw = coverages.ForecastTimeWindow(
        **forecast_time_window_create.model_dump(),
    )
    session.add(db_tw)
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        session.refresh(db_tw)
        return db_tw


def update_forecast_time_window(
    session: sqlmodel.Session,
    db_forecast_time_window: coverages.ForecastTimeWindow,
    forecast_time_window_update: coverages.ForecastTimeWindowUpdate,
) -> coverages.ForecastTimeWindow:
    """Update an forecast time window."""
    for key, value in forecast_time_window_update.model_dump().items():
        setattr(db_forecast_time_window, key, value)
    session.add(db_forecast_time_window)
    session.commit()
    session.refresh(db_forecast_time_window)
    return db_forecast_time_window


def delete_forecast_time_window(
    session: sqlmodel.Session, forecast_time_window_id: int
) -> None:
    db_item = get_forecast_time_window(session, forecast_time_window_id)
    if db_item is not None:
        session.delete(db_item)
        session.commit()
    else:
        raise RuntimeError("Forecast time window not found")


def find_new_station_measurements(
    session: sqlmodel.Session,
    *,
    station_id: int,
    candidates: Sequence[observations.ObservationMeasurementCreate],
) -> list[observations.ObservationMeasurementCreate]:
    """Filter the list of candidate measurements, leaving only those that are new."""
    existing_measurements = collect_all_observation_measurements(
        session, observation_station_id_filter=station_id
    )
    to_drop = []
    for candidate in candidates:
        for existing in existing_measurements:
            if candidate.climatic_indicator_id == existing.climatic_indicator_id:
                if candidate.date == existing.date:
                    to_drop.append(candidate.identifier)
    return [m for m in candidates if m.identifier not in to_drop]
