import functools
import logging
import warnings
from typing import (
    Optional,
    Sequence,
    TYPE_CHECKING,
)

import pandas as pd
import pyloess
import pyproj
from pyproj.enums import TransformDirection
import shapely
from shapely.ops import transform

from .thredds import ncss
from .schemas import (
    dataseries,
    static,
)

if TYPE_CHECKING:
    import datetime as dt
    import httpx
    import numpy as np
    import sqlmodel
    from . import (
        config,
        database,
    )
    from .schemas import (
        coverages,
        observations,
    )

logger = logging.getLogger(__name__)


def generate_derived_forecast_series(
    data_series: dataseries.ForecastDataSeries,
    processing_method: static.CoverageTimeSeriesProcessingMethod,
) -> dataseries.ForecastDataSeries:
    derived_series = dataseries.ForecastDataSeries(
        forecast_coverage=data_series.forecast_coverage,
        dataset_type=data_series.dataset_type,
        processing_method=processing_method,
        temporal_start=data_series.temporal_start,
        temporal_end=data_series.temporal_end,
        location=data_series.location,
    )
    df = data_series.data_.to_frame()
    if processing_method == static.CoverageTimeSeriesProcessingMethod.LOESS_SMOOTHING:
        df[derived_series.identifier] = _apply_loess_smoothing(
            df, data_series.identifier, ignore_warnings=True
        )
    elif (
        processing_method
        == static.CoverageTimeSeriesProcessingMethod.MOVING_AVERAGE_11_YEARS
    ):
        df[derived_series.identifier] = (
            df[data_series.identifier].rolling(center=True, window=11).mean()
        )
    else:
        raise NotImplementedError(
            f"Processing method {processing_method!r} is not implemented"
        )
    derived_series.data_ = df[derived_series.identifier].squeeze()
    return derived_series


def _apply_loess_smoothing(
    df: pd.DataFrame, source_column_name: str, ignore_warnings: bool = True
) -> "np.ndarray":
    with warnings.catch_warnings():
        if ignore_warnings:
            warnings.simplefilter("ignore")
        loess_smoothed = pyloess.loess(
            df.index.year.astype("int").values,
            df[source_column_name],
            span=0.75,
            degree=2,
        )
    return loess_smoothed[:, 1]


def _get_spatial_buffer(
    point_geom: shapely.Point, distance_meters: int
) -> shapely.Polygon:
    """Buffer input point.

    This function expects the input point geometry to be in EPSG:4326 CRS and will
    return a buffer also in the same CRS. However, the buffer's distance is expected
    to be provided in meters. This function takes care of reprojecting the input
    geometry and the output buffer too.
    """
    coordinate_transformer = pyproj.Transformer.from_crs(
        pyproj.CRS("EPSG:4326"), pyproj.CRS("EPSG:3004"), always_xy=True
    ).transform
    forward_coordinate_transformer = functools.partial(
        coordinate_transformer, direction=TransformDirection.FORWARD
    )
    inverse_coordinate_transformer = functools.partial(
        coordinate_transformer, direction=TransformDirection.INVERSE
    )
    point_geom_projected = transform(forward_coordinate_transformer, point_geom)
    buffer_geom_projected = shapely.buffer(
        point_geom_projected, distance=distance_meters
    )
    return transform(inverse_coordinate_transformer, buffer_geom_projected)


def find_nearby_observation_station(
    session: "sqlmodel.Session",
    location: shapely.Point,
    distance_threshold_meters: int,
    observation_series_configuration: Optional[
        "observations.ObservationSeriesConfiguration"
    ] = None,
) -> Optional["observations.ObservationStation"]:
    """
    Find close station that collects data for input series conf's climatic indicator.
    """
    point_buffer_geom = _get_spatial_buffer(location, distance_threshold_meters)
    nearby_stations = database.collect_all_observation_stations(
        session,
        polygon_intersection_filter=point_buffer_geom,
        climatic_indicator_id_filter=(
            observation_series_configuration.climatic_indicator_id
            if observation_series_configuration is not None
            else None
        ),
    )
    return nearby_stations[0] if len(nearby_stations) > 0 else None


def get_nearby_observation_station_time_series(
    session: "sqlmodel.Session",
    location: shapely.Point,
    observation_series_configuration: "observations.ObservationSeriesConfiguration",
    distance_threshold_meters: int,
    temporal_range: tuple[Optional["dt.datetime"], Optional["dt.datetime"]],
) -> Optional[dataseries.ObservationStationDataSeries]:
    result = None
    nearby_station = find_nearby_observation_station(
        session, location, distance_threshold_meters, observation_series_configuration
    )
    if nearby_station is not None:
        result = dataseries.ObservationStationDataSeries(
            observation_series_configuration=observation_series_configuration,
            observation_station=nearby_station,
            processing_method=static.ObservationTimeSeriesProcessingMethod.NO_PROCESSING,
        )
        raw_data = database.collect_all_observation_measurements(
            session,
            observation_station_id_filter=nearby_station.id,
            climatic_indicator_id_filter=observation_series_configuration.climatic_indicator_id,
            aggregation_type_filter=observation_series_configuration.measurement_aggregation_type,
        )
        if len(raw_data) > 0:
            parsed_data = parse_observation_station_data(
                raw_data,
                base_name=result.identifier,
                temporal_range=temporal_range,
            )
            result.data_ = parsed_data
        else:
            result = None
    else:
        logger.info(
            f"Could not find any observation station within a "
            f"{distance_threshold_meters} meter radius of {location!r} "
            f"with suitable data"
        )
    return result


def parse_observation_station_data(
    raw_data: Sequence["observations.ObservationMeasurement"],
    base_name: str,
    temporal_range: tuple[Optional["dt.datetime"], Optional["dt.datetime"]],
) -> pd.Series:
    df = pd.DataFrame([i.model_dump() for i in raw_data])
    df = df.rename(
        columns={
            "value": base_name,
            "date": "time",
        },
    )
    df = df[[base_name, "time"]]
    df.set_index("time", inplace=True)
    if temporal_range is not None:
        start, end = temporal_range
        if start is not None:
            df = df[start:]
        if end is not None:
            df = df[:end]
    return df.squeeze()


def get_forecast_coverage_time_series(
    *,
    settings: "config.ArpavPpcvSettings",
    session: "sqlmodel.Session",
    http_client: "httpx.Client",
    coverage: "coverages.ForecastCoverageInternal",
    point_geom: "shapely.Point",
    temporal_range: tuple[Optional["dt.datetime"], Optional["dt.datetime"]],
    forecast_coverage_processing_methods: list[
        "static.CoverageTimeSeriesProcessingMethod"
    ],
    observation_processing_methods: list[
        "static.ObservationTimeSeriesProcessingMethod"
    ],
    include_coverage_data: bool = True,
    include_observation_data: bool = False,
    include_coverage_uncertainty: bool = False,
    include_coverage_related_models: bool = False,
) -> tuple[
    Optional[list[dataseries.ForecastDataSeries]],
    Optional[list[dataseries.ObservationStationDataSeries]],
]:
    coverage_series = None
    observation_series = None
    if include_coverage_data:
        coverage_series = _get_forecast_coverage_coverage_time_series(
            settings.thredds_server,
            session,
            http_client,
            coverage,
            point_geom,
            forecast_coverage_processing_methods,
            include_coverage_uncertainty,
            include_coverage_related_models,
            temporal_range=temporal_range,
        )
    if include_observation_data:
        observation_series = _get_forecast_coverage_observation_time_series(
            settings,
            session,
            coverage,
            point_geom,
            observation_processing_methods,
            temporal_range=temporal_range,
        )
    return coverage_series, observation_series


def generate_derived_observation_series(
    series: dataseries.ObservationStationDataSeries,
    processing_method: static.ObservationTimeSeriesProcessingMethod,
    derived_series_name: Optional[str] = None,
) -> tuple[pd.DataFrame, str]:
    column_to_process = series.identifier
    derived_name = (
        derived_series_name
        if derived_series_name
        else "__".join((column_to_process, processing_method.value))
    )
    df = pd.to_frame(series.data_)
    if (
        processing_method
        == static.ObservationTimeSeriesProcessingMethod.MOVING_AVERAGE_5_YEARS
    ):
        df[derived_name] = df[column_to_process].rolling(window=5, center=True).mean()
    else:
        raise NotImplementedError(
            f"Processing method {processing_method!r} is not implemented"
        )
    return df, derived_name


def _get_forecast_coverage_coverage_time_series(
    thredds_settings: "config.ThreddsServerSettings",
    session: "sqlmodel.Session",
    http_client: "httpx.Client",
    forecast_coverage: "coverages.ForecastCoverageInternal",
    point_geom: shapely.Point,
    processing_methods: Sequence[static.CoverageTimeSeriesProcessingMethod],
    include_uncertainty: bool,
    include_related_models: bool,
    temporal_range: tuple[Optional["dt.datetime"], Optional["dt.datetime"]],
) -> list[dataseries.ForecastDataSeries]:
    data_ = []
    cov_series = _retrieve_forecast_coverage_data(
        http_client,
        thredds_settings,
        forecast_coverage,
        point_geom,
        temporal_range,
        include_uncertainty=include_uncertainty,
    )
    for item in [i for i in cov_series if i is not None]:
        data_.append(item)
    if include_related_models:
        for other_cov in database.generate_forecast_coverages_for_other_models(
            session, forecast_coverage
        ):
            other_cov_series = _retrieve_forecast_coverage_data(
                http_client,
                thredds_settings,
                other_cov,
                point_geom,
                temporal_range,
                include_uncertainty=include_uncertainty,
            )
            for item in [i for i in other_cov_series if i is not None]:
                data_.append(item)
    result = []
    for cov_data_series in data_:
        result.append(cov_data_series)
        for processing_method in [
            pm
            for pm in processing_methods
            if pm != static.CoverageTimeSeriesProcessingMethod.NO_PROCESSING
        ]:
            derived_series = generate_derived_forecast_series(
                cov_data_series,
                processing_method,
            )
            result.append(derived_series)
    return result


def _get_forecast_coverage_observation_time_series(
    settings: "config.ArpavPpcvSettings",
    session: "sqlmodel.Session",
    coverage: "coverages.ForecastCoverageInternal",
    point_geom: shapely.Point,
    processing_methods: list[static.ObservationTimeSeriesProcessingMethod],
    temporal_range: tuple[Optional["dt.datetime"], Optional["dt.datetime"]],
) -> list[dataseries.ObservationStationDataSeries]:
    result = {}
    for osc_link in coverage.configuration.observation_series_configuration_links:
        observation_series_conf = osc_link.observation_series_configuration
        observation_data_series = get_nearby_observation_station_time_series(
            session,
            point_geom,
            observation_series_conf,
            distance_threshold_meters=settings.nearest_station_radius_meters,
            temporal_range=temporal_range,
        )
        if observation_data_series is not None:
            result[observation_data_series.identifier] = observation_data_series
            for processing_method in processing_methods:
                if (
                    processing_method
                    == static.ObservationTimeSeriesProcessingMethod.NO_PROCESSING
                ):
                    continue  # already generated
                else:
                    series = dataseries.ObservationStationDataSeries(
                        observation_series_configuration=observation_series_conf,
                        observation_station=observation_data_series.observation_station,
                        processing_method=processing_method,
                    )
                    smoothed_df, col_name = generate_derived_observation_series(
                        observation_data_series,
                        processing_method,
                        derived_series_name=series.identifier,
                    )
                    series.data_ = smoothed_df[series.identifier].squeeze()
                    result[series.identifier] = series
        else:
            logger.info("No station data found, skipping...")
    else:
        logger.info(
            "Cannot include observation data - no climatic indicator is related "
            "to this coverage configuration"
        )
    return result


def _retrieve_forecast_coverage_data(
    http_client: "httpx.Client",
    settings: "config.ThreddsServerSettings",
    coverage: "coverages.ForecastCoverageInternal",
    point_geom: shapely.Point,
    temporal_range: tuple[Optional["dt.datetime"], Optional["dt.datetime"]],
    include_uncertainty: bool = False,
) -> tuple[
    dataseries.ForecastDataSeries | None,
    dataseries.ForecastDataSeries | None,
    dataseries.ForecastDataSeries | None,
]:
    retriever = ncss.ForecastCoverageDataRetriever(
        settings=settings,
        http_client=http_client,
        coverage=coverage,
    )
    main_series = dataseries.ForecastDataSeries(
        forecast_coverage=coverage,
        dataset_type=static.ForecastDatasetType.MAIN,
        processing_method=static.CoverageTimeSeriesProcessingMethod.NO_PROCESSING,
        temporal_start=temporal_range[0],
        temporal_end=temporal_range[1],
        location=point_geom,
    )
    lower_uncert_series = None
    upper_uncert_series = None
    main_data = retriever.retrieve_main_data(
        point_geom, temporal_range, target_series_name=main_series.identifier
    )
    if main_data is not None:
        main_series.data_ = main_data
        if include_uncertainty:
            lower_uncert_series = dataseries.ForecastDataSeries(
                forecast_coverage=coverage,
                dataset_type=static.ForecastDatasetType.LOWER_UNCERTAINTY,
                processing_method=static.CoverageTimeSeriesProcessingMethod.NO_PROCESSING,
                temporal_start=temporal_range[0],
                temporal_end=temporal_range[1],
                location=point_geom,
            )
            lower_uncert_data = retriever.retrieve_lower_uncertainty_data(
                point_geom,
                temporal_range,
                target_series_name=lower_uncert_series.identifier,
            )
            if lower_uncert_data is not None:
                lower_uncert_series.data_ = lower_uncert_data
            else:
                lower_uncert_series = None
            upper_uncert_series = dataseries.ForecastDataSeries(
                forecast_coverage=coverage,
                dataset_type=static.ForecastDatasetType.UPPER_UNCERTAINTY,
                processing_method=static.CoverageTimeSeriesProcessingMethod.NO_PROCESSING,
                temporal_start=temporal_range[0],
                temporal_end=temporal_range[1],
                location=point_geom,
            )
            upper_uncert_data = retriever.retrieve_upper_uncertainty_data(
                point_geom,
                temporal_range,
                target_series_name=upper_uncert_series.identifier,
            )
            if upper_uncert_data is not None:
                upper_uncert_series.data_ = upper_uncert_data
            else:
                upper_uncert_series = None
    else:
        main_series = None
    return main_series, lower_uncert_series, upper_uncert_series


def get_overview_coverage_time_series(
    *,
    settings: "config.ArpavPpcvSettings",
    session: "sqlmodel.Session",
    coverage: "coverages.OverviewCoverageInternal",
    processing_methods: list[static.CoverageTimeSeriesProcessingMethod],
    include_uncertainty: bool,
) -> list[dataseries.OverviewDataSeries]:
    covs = database.collect_all_coverages(
        session,
        configuration_parameter_values_filter=[
            database.get_configuration_parameter_value_by_names(
                session, base.CoreConfParamName.ARCHIVE.value, "barometro_climatico"
            )
        ],
    )
    additional_smoothing_strategies = [
        ss
        for ss in smoothing_strategies
        if ss != static.CoverageTimeSeriesProcessingMethod.NO_PROCESSING
    ]
    dfs = []
    for cov in covs:
        is_uncertainty_cov = False
        for used_value in cov.configuration.possible_values:
            if (
                    used_value.configuration_parameter_value.configuration_parameter.name
                    == CoreConfParamName.UNCERTAINTY_TYPE.value
            ):
                is_uncertainty_cov = True
        if not is_uncertainty_cov:
            df = _get_climate_barometer_data(settings, cov)
            dfs.append((cov, df))

        if include_uncertainty:
            lower_cov, upper_cov = get_related_uncertainty_coverage_configurations(
                session, cov
            )
            if lower_cov is not None:
                lower_df = _get_climate_barometer_data(settings, lower_cov)
                dfs.append((lower_cov, lower_df))
            if upper_cov is not None:
                upper_df = _get_climate_barometer_data(settings, upper_cov)
                dfs.append((upper_cov, upper_df))
    result = {}
    for cov, df in dfs:
        result[(cov, static.CoverageTimeSeriesProcessingMethod.NO_PROCESSING)] = df[
            cov.identifier
        ].squeeze()
        for strategy in additional_smoothing_strategies:
            df, smoothed_col = process_coverage_smoothing_strategy(
                df, cov.identifier, strategy
            )
            result[(cov, strategy)] = df[smoothed_col].squeeze()
    return result
