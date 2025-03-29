import datetime as dt
import functools
import logging
import warnings
from typing import (
    cast,
    Optional,
    Sequence,
    TYPE_CHECKING,
)

import pandas as pd
import pyloess
import pymannkendall
import pyproj
from pyproj.enums import TransformDirection
import shapely
from shapely.ops import transform

from . import db
from .thredds import (
    ncss,
    opendap,
)
from .schemas import (
    dataseries,
    static,
)

if TYPE_CHECKING:
    import httpx
    import numpy as np
    import sqlmodel
    from . import (
        config,
    )
    from .schemas import (
        coverages,
        observations,
        overviews,
    )

logger = logging.getLogger(__name__)


def generate_derived_overview_series(
    data_series: dataseries.OverviewDataSeriesProtocol,
    processing_method: static.CoverageTimeSeriesProcessingMethod,
) -> dataseries.OverviewDataSeriesProtocol:
    derived_series = data_series.replace(
        processing_method=processing_method, data_=None
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


def _generate_decade_series(
    original: pd.DataFrame,
    original_column: str,
    column_name: str,
) -> pd.DataFrame:
    # group values by climatological decade, which starts at year 1 and ends at year 10
    decade_grouper = original.groupby(((original.index.year - 1) // 10) * 10)
    decade_df = decade_grouper.agg(
        num_values=(original_column, "size"),
        **{column_name: (original_column, "mean")},
    )
    # discard decades where there are less than 7 years
    decade_df = decade_df[decade_df.num_values >= 7]
    decade_df = decade_df.drop(columns=["num_values"])
    decade_df["time"] = pd.to_datetime(decade_df.index.astype(str), utc=True)
    decade_df.set_index("time", inplace=True)
    return decade_df


def _generate_mann_kendall_series(
    original: pd.DataFrame,
    original_column: str,
    column_name: str,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
) -> tuple[pd.DataFrame, dict]:
    mk_start = start_year or original.index[0].year
    mk_end = end_year or original.index[-1].year
    mk_df = original[str(mk_start) : str(mk_end)].copy()
    mk_result = pymannkendall.original_test(mk_df[original_column])
    mk_df[column_name] = (
        mk_result.slope * (mk_df.index.year - mk_df.index.year.min())
        + mk_result.intercept
    )
    return mk_df, {
        "start_year": mk_start,
        "end_year": mk_end,
        "trend": mk_result.trend,
        "h": bool(mk_result.h),
        "p": mk_result.p,
        "z": mk_result.z,
        "tau": mk_result.Tau,
        "s": mk_result.s,
        "var_s": mk_result.var_s,
        "slope": mk_result.slope,
        "intercept": mk_result.intercept,
        "is_statistically_significant": bool(mk_result.p < 0.05),
    }


def generate_derived_forecast_series(
    data_series: dataseries.ForecastDataSeries,
    processing_method: static.CoverageTimeSeriesProcessingMethod,
) -> dataseries.ForecastDataSeries:
    derived_series = dataseries.ForecastDataSeries(
        coverage=data_series.coverage,
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
    nearby_stations = db.collect_all_observation_stations(
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
    temporal_range: tuple[Optional[dt.datetime], Optional[dt.datetime]],
) -> Optional[dataseries.ObservationStationDataSeries]:
    result = None
    nearby_station = find_nearby_observation_station(
        session, location, distance_threshold_meters, observation_series_configuration
    )
    if nearby_station is not None:
        result = dataseries.ObservationStationDataSeries(
            observation_series_configuration=observation_series_configuration,
            dataset_type=static.DatasetType.OBSERVATION,
            observation_station=nearby_station,
            processing_method=static.ObservationTimeSeriesProcessingMethod.NO_PROCESSING,
            location=location,
        )
        raw_data = db.collect_all_observation_measurements(
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
    temporal_range: tuple[Optional[dt.datetime], Optional[dt.datetime]],
) -> pd.Series:
    df = pd.DataFrame([i.model_dump() for i in raw_data])
    df = df.rename(
        columns={
            "value": base_name,
            "date": "time",
        },
    )
    df = df[[base_name, "time"]]
    df["time"] = pd.to_datetime(df["time"])
    df.set_index("time", inplace=True)
    if temporal_range is not None:
        start, end = temporal_range
        if start is not None:
            df = df[start:]
        if end is not None:
            df = df[:end]
    return df.squeeze()


def generate_decade_derived_observation_station_series(
    original_series: dataseries.ObservationStationDataSeries,
    point_geom: shapely.geometry.Point,
) -> dataseries.ObservationStationDataSeries:
    derived_series = dataseries.ObservationStationDataSeries(
        observation_series_configuration=(
            original_series.observation_series_configuration
        ),
        observation_station=original_series.observation_station,
        dataset_type=original_series.dataset_type,
        processing_method=(
            static.HistoricalTimeSeriesProcessingMethod.DECADE_AGGREGATION
        ),
        location=point_geom,
    )
    df = original_series.data_.to_frame()
    df = _generate_decade_series(
        df, original_series.identifier, derived_series.identifier
    )
    derived_series.data_ = df[derived_series.identifier].squeeze()
    return derived_series


def generate_loess_derived_observation_station_series(
    original_series: dataseries.ObservationStationDataSeries,
    point_geom: shapely.geometry.Point,
) -> dataseries.ObservationStationDataSeries:
    derived_series = dataseries.ObservationStationDataSeries(
        observation_series_configuration=(
            original_series.observation_series_configuration
        ),
        observation_station=original_series.observation_station,
        dataset_type=original_series.dataset_type,
        processing_method=(static.HistoricalTimeSeriesProcessingMethod.LOESS_SMOOTHING),
        location=point_geom,
    )
    df = original_series.data_.to_frame()
    df[derived_series.identifier] = _apply_loess_smoothing(
        df, original_series.identifier, ignore_warnings=True
    )
    derived_series.data_ = df[derived_series.identifier].squeeze()
    return derived_series


def generate_moving_average_derived_observation_station_series(
    original_series: dataseries.ObservationStationDataSeries,
    point_geom: shapely.geometry.Point,
) -> dataseries.ObservationStationDataSeries:
    derived_series = dataseries.ObservationStationDataSeries(
        observation_series_configuration=(
            original_series.observation_series_configuration
        ),
        observation_station=original_series.observation_station,
        dataset_type=original_series.dataset_type,
        processing_method=(
            static.HistoricalTimeSeriesProcessingMethod.MOVING_AVERAGE_5_YEARS
        ),
        location=point_geom,
    )
    df = original_series.data_.to_frame()
    df[derived_series.identifier] = (
        df[original_series.identifier].rolling(window=5, center=True).mean()
    )
    derived_series.data_ = df[derived_series.identifier].squeeze()
    return derived_series


def generate_mann_kendall_derived_observation_station_series(
    original_series: dataseries.ObservationStationDataSeries,
    point_geom: shapely.geometry.Point,
    *,
    start: dt.datetime | None,
    end: dt.datetime | None,
) -> dataseries.ObservationStationDataSeries:
    derived_series = dataseries.ObservationStationDataSeries(
        observation_series_configuration=(
            original_series.observation_series_configuration
        ),
        observation_station=original_series.observation_station,
        dataset_type=original_series.dataset_type,
        processing_method=(
            static.HistoricalTimeSeriesProcessingMethod.MANN_KENDALL_TREND
        ),
        location=point_geom,
    )
    df = original_series.data_.to_frame()
    mk_start = start or df.index[0].year
    mk_end = end or df.index[-1].year
    df, info = _generate_mann_kendall_series(
        df, original_series.identifier, derived_series.identifier, mk_start, mk_end
    )
    derived_series.processing_method_info = info
    derived_series.data_ = df[derived_series.identifier].squeeze()
    return derived_series


def generate_moving_average_derived_historical_coverage_series(
    original_series: dataseries.HistoricalDataSeries,
) -> dataseries.HistoricalDataSeries:
    derived_series = dataseries.HistoricalDataSeries(
        coverage=original_series.coverage,
        dataset_type=original_series.dataset_type,
        processing_method=static.HistoricalTimeSeriesProcessingMethod.MOVING_AVERAGE_5_YEARS,
        temporal_start=original_series.temporal_start,
        temporal_end=original_series.temporal_end,
        location=original_series.location,
    )
    df = original_series.data_.to_frame()
    df[derived_series.identifier] = (
        df[original_series.identifier].rolling(center=True, window=5).mean()
    )
    derived_series.data_ = df[derived_series.identifier].squeeze()
    return derived_series


def generate_decade_derived_historical_coverage_series(
    original_series: dataseries.HistoricalDataSeries,
) -> dataseries.HistoricalDataSeries:
    derived_series = dataseries.HistoricalDataSeries(
        coverage=original_series.coverage,
        dataset_type=original_series.dataset_type,
        processing_method=static.HistoricalTimeSeriesProcessingMethod.DECADE_AGGREGATION,
        temporal_start=original_series.temporal_start,
        temporal_end=original_series.temporal_end,
        location=original_series.location,
    )
    df = original_series.data_.to_frame()
    df = _generate_decade_series(
        df, original_series.identifier, derived_series.identifier
    )
    derived_series.data_ = df[derived_series.identifier].squeeze()
    return derived_series


def generate_loess_derived_historical_coverage_series(
    original_series: dataseries.HistoricalDataSeries,
) -> dataseries.HistoricalDataSeries:
    derived_series = dataseries.HistoricalDataSeries(
        coverage=original_series.coverage,
        dataset_type=original_series.dataset_type,
        processing_method=static.HistoricalTimeSeriesProcessingMethod.LOESS_SMOOTHING,
        temporal_start=original_series.temporal_start,
        temporal_end=original_series.temporal_end,
        location=original_series.location,
    )
    df = original_series.data_.to_frame()
    df[derived_series.identifier] = _apply_loess_smoothing(
        df, original_series.identifier, ignore_warnings=True
    )
    derived_series.data_ = df[derived_series.identifier].squeeze()
    return derived_series


def generate_mann_kendall_derived_historical_coverage_series(
    original_series: dataseries.HistoricalDataSeries,
    *,
    start: dt.datetime | None,
    end: dt.datetime | None,
) -> dataseries.HistoricalDataSeries:
    derived_series = dataseries.HistoricalDataSeries(
        coverage=original_series.coverage,
        dataset_type=original_series.dataset_type,
        processing_method=static.HistoricalTimeSeriesProcessingMethod.MANN_KENDALL_TREND,
        temporal_start=original_series.temporal_start,
        temporal_end=original_series.temporal_end,
        location=original_series.location,
    )
    df = original_series.data_.to_frame()
    mk_start = start or df.index[0].year
    mk_end = end or df.index[-1].year
    df, info = _generate_mann_kendall_series(
        df, original_series.identifier, derived_series.identifier, mk_start, mk_end
    )
    derived_series.processing_method_info = info
    derived_series.data_ = df[derived_series.identifier].squeeze()
    return derived_series


def get_historical_time_series(
    *,
    settings: "config.ArpavPpcvSettings",
    session: "sqlmodel.Session",
    http_client: "httpx.Client",
    coverage: "coverages.HistoricalCoverageInternal",
    point_geom: "shapely.Point",
    temporal_range: tuple[Optional[dt.datetime], Optional[dt.datetime]],
    mann_kendall_params: dataseries.MannKendallParameters,
    include_moving_average_series: bool,
    include_decade_aggregation_series: bool,
    include_loess_series: bool,
) -> list[dataseries.HistoricalDataSeries | dataseries.ObservationStationDataSeries]:
    """Return a list of historical time series for the input location.

    If there is a nearby observation station, returns station data. Otherwise
    returns NetCDF coverage data
    """
    # if the related observation series configuration specifies a different climatic
    # indicator try to retrieve historical data instead
    relevant_series_confs = [
        oscl.observation_series_configuration
        for oscl in coverage.configuration.observation_series_configuration_links
        if (
            coverage.configuration.climatic_indicator.identifier
            == oscl.observation_series_configuration.climatic_indicator.identifier
        )
    ]

    result = []
    for obs_series_conf in relevant_series_confs:
        obs_data_series = get_nearby_observation_station_time_series(
            session,
            point_geom,
            obs_series_conf,
            distance_threshold_meters=settings.nearest_station_radius_meters,
            temporal_range=temporal_range,
        )
        if obs_data_series is not None:
            result.append(obs_data_series)
            if include_loess_series:
                result.append(
                    generate_loess_derived_observation_station_series(
                        obs_data_series, point_geom
                    )
                )
            if include_moving_average_series:
                result.append(
                    generate_moving_average_derived_observation_station_series(
                        obs_data_series, point_geom
                    )
                )
            if include_decade_aggregation_series:
                result.append(
                    generate_decade_derived_observation_station_series(
                        obs_data_series, point_geom
                    )
                )
            if mann_kendall_params is not None:
                result.append(
                    generate_mann_kendall_derived_observation_station_series(
                        obs_data_series,
                        point_geom,
                        start=mann_kendall_params.start_year,
                        end=mann_kendall_params.end_year,
                    )
                )
        else:
            logger.info("No station data found")
    if len(result) == 0:
        # could not find any nearby stations, let's fetch historical coverage data
        cov_series = _retrieve_historical_coverage_data(
            http_client, settings.thredds_server, coverage, point_geom, temporal_range
        )
        if cov_series is not None:
            result.append(cov_series)
            if include_loess_series:
                result.append(
                    generate_loess_derived_historical_coverage_series(cov_series)
                )
            if include_moving_average_series:
                result.append(
                    generate_moving_average_derived_historical_coverage_series(
                        cov_series
                    )
                )
            if include_decade_aggregation_series:
                result.append(
                    generate_decade_derived_historical_coverage_series(cov_series)
                )
            if mann_kendall_params is not None:
                result.append(
                    generate_mann_kendall_derived_historical_coverage_series(
                        cov_series,
                        start=mann_kendall_params.start_year,
                        end=mann_kendall_params.end_year,
                    )
                )
    return result


def get_forecast_coverage_time_series(
    *,
    settings: "config.ArpavPpcvSettings",
    session: "sqlmodel.Session",
    http_client: "httpx.Client",
    coverage: "coverages.ForecastCoverageInternal",
    point_geom: "shapely.Point",
    temporal_range: tuple[Optional[dt.datetime], Optional[dt.datetime]],
    coverage_processing_methods: list[static.CoverageTimeSeriesProcessingMethod],
    observation_processing_methods: list[static.ObservationTimeSeriesProcessingMethod],
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
            coverage_processing_methods,
            include_coverage_uncertainty,
            include_coverage_related_models,
            temporal_range=temporal_range,
        )
    if include_observation_data:
        # do not gather time series if the related observation series configuration
        # specifies a different climatic indicator
        relevant_series_confs = [
            oscl.observation_series_configuration
            for oscl in coverage.configuration.observation_series_configuration_links
            if (
                coverage.configuration.climatic_indicator.identifier
                == oscl.observation_series_configuration.climatic_indicator.identifier
            )
        ]
        observation_series = _get_forecast_coverage_observation_time_series(
            settings=settings,
            session=session,
            observation_series_configurations=relevant_series_confs,
            point_geom=point_geom,
            processing_methods=observation_processing_methods,
            temporal_range=temporal_range,
        )
    return coverage_series, observation_series


def generate_derived_observation_series(
    data_series: dataseries.ObservationStationDataSeries,
    processing_method: static.ObservationTimeSeriesProcessingMethod,
    derived_series_name: Optional[str] = None,
) -> tuple[pd.DataFrame, str]:
    column_to_process = data_series.identifier
    derived_name = (
        derived_series_name
        if derived_series_name
        else "__".join((column_to_process, processing_method.value))
    )
    df = data_series.data_.to_frame()
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
    temporal_range: tuple[Optional[dt.datetime], Optional[dt.datetime]],
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
        for other_cov in db.generate_forecast_coverages_for_other_models(
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
    observation_series_configurations: list[
        "observations.ObservationSeriesConfiguration"
    ],
    point_geom: shapely.Point,
    processing_methods: list[static.ObservationTimeSeriesProcessingMethod],
    temporal_range: tuple[Optional[dt.datetime], Optional[dt.datetime]],
) -> list[dataseries.ObservationStationDataSeries]:
    result = []
    for observation_series_conf in observation_series_configurations:
        observation_data_series = get_nearby_observation_station_time_series(
            session,
            point_geom,
            observation_series_conf,
            distance_threshold_meters=settings.nearest_station_radius_meters,
            temporal_range=temporal_range,
        )
        if observation_data_series is not None:
            result.append(observation_data_series)
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
                        dataset_type=observation_data_series.dataset_type,
                        processing_method=processing_method,
                        location=point_geom,
                    )
                    smoothed_df, col_name = generate_derived_observation_series(
                        observation_data_series,
                        processing_method,
                        derived_series_name=series.identifier,
                    )
                    series.data_ = smoothed_df[series.identifier].squeeze()
                    result.append(series)
        else:
            logger.info("No station data found, skipping...")
    else:
        logger.info(
            "Cannot include observation data - no climatic indicator is related "
            "to this coverage configuration"
        )
    return result


def _retrieve_historical_coverage_data(
    http_client: "httpx.Client",
    settings: "config.ThreddsServerSettings",
    coverage: "coverages.HistoricalCoverageInternal",
    point_geom: shapely.Point,
    temporal_range: tuple[Optional[dt.datetime], Optional[dt.datetime]],
) -> Optional[dataseries.HistoricalDataSeries]:
    retriever = ncss.SimpleCoverageDataRetriever(
        settings=settings,
        http_client=http_client,
        coverage=cast(ncss.RetrievableCoverageProtocol, coverage),
    )
    main_series = dataseries.HistoricalDataSeries(
        coverage=coverage,
        dataset_type=static.DatasetType.MAIN,
        processing_method=static.HistoricalTimeSeriesProcessingMethod.NO_PROCESSING,
        temporal_start=temporal_range[0],
        temporal_end=temporal_range[1],
        location=point_geom,
    )
    main_data = retriever.retrieve_main_data(
        point_geom, temporal_range, target_series_name=main_series.identifier
    )
    if main_data is not None:
        main_series.data_ = main_data
    else:
        main_series = None
    return main_series


def _retrieve_forecast_coverage_data(
    http_client: "httpx.Client",
    settings: "config.ThreddsServerSettings",
    coverage: "coverages.ForecastCoverageInternal",
    point_geom: shapely.Point,
    temporal_range: tuple[Optional[dt.datetime], Optional[dt.datetime]],
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
        coverage=coverage,
        dataset_type=static.DatasetType.MAIN,
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
                coverage=coverage,
                dataset_type=static.DatasetType.LOWER_UNCERTAINTY,
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
                coverage=coverage,
                dataset_type=static.DatasetType.UPPER_UNCERTAINTY,
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


def get_overview_time_series(
    *,
    settings: "config.ArpavPpcvSettings",
    session: "sqlmodel.Session",
    processing_methods: list[static.CoverageTimeSeriesProcessingMethod],
    include_uncertainty: bool,
) -> tuple[
    list[dataseries.ForecastOverviewDataSeries],
    list[dataseries.ObservationOverviewDataSeries],
]:
    forecast_series_confs = db.collect_all_forecast_overview_series_configurations(
        session
    )

    forecast_overview_data_series = []
    for forecast_series_conf in forecast_series_confs:
        forecast_series = db.generate_forecast_overview_series_from_configuration(
            forecast_series_conf
        )
        for series in forecast_series:
            forecast_overview_data_series.extend(
                get_forecast_overview_time_series(
                    settings=settings.thredds_server,
                    overview_series=series,
                    processing_methods=processing_methods,
                    include_uncertainty=include_uncertainty,
                )
            )
    observation_overview_data_series = []
    observation_series_confs = (
        db.collect_all_observation_overview_series_configurations(session)
    )
    for observation_series_conf in observation_series_confs:
        observation_series = db.generate_observation_overview_series_from_configuration(
            observation_series_conf
        )
        observation_overview_data_series.extend(
            get_observation_overview_time_series(
                settings=settings.thredds_server,
                overview_series=observation_series,
                processing_methods=processing_methods,
            )
        )
    return forecast_overview_data_series, observation_overview_data_series


def get_observation_overview_time_series(
    *,
    settings: "config.ThreddsServerSettings",
    overview_series: "overviews.ObservationOverviewSeriesInternal",
    processing_methods: list[static.CoverageTimeSeriesProcessingMethod],
) -> list[dataseries.ObservationOverviewDataSeries]:
    series = _retrieve_observation_overview_data(settings, overview_series)
    result = []
    if series is not None:
        result.append(series)
        for processing_method in (
            pm
            for pm in processing_methods
            if pm != static.CoverageTimeSeriesProcessingMethod.NO_PROCESSING
        ):
            derived_series = generate_derived_overview_series(series, processing_method)
            result.append(derived_series)
    return result


def get_forecast_overview_time_series(
    *,
    settings: "config.ThreddsServerSettings",
    overview_series: "overviews.ForecastOverviewSeriesInternal",
    processing_methods: list[static.CoverageTimeSeriesProcessingMethod],
    include_uncertainty: bool,
) -> list[dataseries.ForecastOverviewDataSeries]:
    data_ = []
    series = _retrieve_forecast_overview_data(
        settings, overview_series, include_uncertainty
    )
    for item in [i for i in series if i is not None]:
        data_.append(item)
    result = []
    for overview_series in data_:
        result.append(overview_series)
        for processing_method in (
            pm
            for pm in processing_methods
            if pm != static.CoverageTimeSeriesProcessingMethod.NO_PROCESSING
        ):
            derived_series = generate_derived_overview_series(
                overview_series, processing_method
            )
            result.append(derived_series)
    return result


def _retrieve_forecast_overview_data(
    settings: "config.ThreddsServerSettings",
    overview_series: "overviews.ForecastOverviewSeriesInternal",
    include_uncertainty: bool,
) -> tuple[
    dataseries.ForecastOverviewDataSeries | None,
    dataseries.ForecastOverviewDataSeries | None,
    dataseries.ForecastOverviewDataSeries | None,
]:
    retriever = opendap.ForecastOverviewDataRetriever(
        settings=settings,
        overview_series=overview_series,
    )
    main_series = dataseries.ForecastOverviewDataSeries(
        overview_series=overview_series,
        processing_method=static.CoverageTimeSeriesProcessingMethod.NO_PROCESSING,
        dataset_type=static.DatasetType.MAIN,
    )
    lower_uncert_series = None
    upper_uncert_series = None
    main_data = retriever.retrieve_main_data(main_series.identifier)
    if main_data is not None:
        main_series.data_ = main_data
        if include_uncertainty:
            lower_uncert_series = dataseries.ForecastOverviewDataSeries(
                overview_series=overview_series,
                processing_method=static.CoverageTimeSeriesProcessingMethod.NO_PROCESSING,
                dataset_type=static.DatasetType.LOWER_UNCERTAINTY,
            )
            lower_uncert_data = retriever.retrieve_lower_uncertainty_data(
                lower_uncert_series.identifier
            )
            if lower_uncert_data is not None:
                lower_uncert_series.data_ = lower_uncert_data
            else:
                lower_uncert_series = None
            upper_uncert_series = dataseries.ForecastOverviewDataSeries(
                overview_series=overview_series,
                processing_method=static.CoverageTimeSeriesProcessingMethod.NO_PROCESSING,
                dataset_type=static.DatasetType.UPPER_UNCERTAINTY,
            )
            upper_uncert_data = retriever.retrieve_upper_uncertainty_data(
                upper_uncert_series.identifier
            )
            if upper_uncert_data is not None:
                upper_uncert_series.data_ = upper_uncert_data
            else:
                upper_uncert_series = None
    return main_series, lower_uncert_series, upper_uncert_series


def _retrieve_observation_overview_data(
    settings: "config.ThreddsServerSettings",
    overview_series: "overviews.ObservationOverviewSeriesInternal",
) -> Optional[dataseries.ObservationOverviewDataSeries]:
    retriever = opendap.ObservationOverviewDataRetriever(
        settings=settings,
        overview_series=overview_series,
    )
    main_series = dataseries.ObservationOverviewDataSeries(
        overview_series=overview_series,
        processing_method=static.CoverageTimeSeriesProcessingMethod.NO_PROCESSING,
        dataset_type=static.DatasetType.MAIN,
    )
    main_data = retriever.retrieve_main_data(main_series.identifier)
    if main_data is not None:
        main_series.data_ = main_data
    else:
        main_series = None
    return main_series
