"""Database utilities."""

import datetime as dt
import itertools
import logging
from typing import (
    Optional,
    Sequence,
)

import geohashr
import geojson_pydantic
import shapely
import shapely.io
import sqlalchemy
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
    raw_ds_type, raw_location, raw_start, raw_end, raw_processing_method = identifier
    try:
        dataset_type = static.DatasetType(raw_ds_type)
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
        processing_method = static.CoverageTimeSeriesProcessingMethod(
            raw_processing_method
        )
    except ValueError:
        raise exceptions.InvalidForecastCoverageDataSeriesIdentifierError(
            f"Processing method {raw_processing_method} does not exist"
        )
    return dataseries.ForecastDataSeries(
        forecast_coverage=forecast_coverage,
        dataset_type=dataset_type,
        processing_method=processing_method,
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
    if parts[0] == static.DataCategory.FORECAST.value:
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
