import datetime as dt
import functools
import io
import logging
import warnings
from typing import Optional

import anyio
import anyio.to_thread
import cftime
import httpx
import netCDF4
import numpy as np
import pandas as pd
import pyloess
import pymannkendall as mk
import pyproj
import shapely
import shapely.io
import sqlmodel
from anyio.from_thread import start_blocking_portal
from arpav_ppcv.schemas.base import CoreConfParamName
from dateutil.parser import isoparse
from geoalchemy2.shape import to_shape
from pandas.core.indexes.datetimes import DatetimeIndex
from pyproj.enums import TransformDirection
from shapely.ops import transform

from . import (
    config,
    database,
)
from .schemas import (
    base,
    coverages,
    observations,
)
from .thredds import (
    crawler,
    ncss,
)

logger = logging.getLogger(__name__)


def get_climate_barometer_time_series(
    settings: config.ArpavPpcvSettings,
    session: sqlmodel.Session,
    smoothing_strategies: list[base.CoverageDataSmoothingStrategy],
    include_uncertainty: bool,
) -> dict[
    tuple[coverages.CoverageInternal, base.CoverageDataSmoothingStrategy], pd.Series
]:
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
        if ss != base.CoverageDataSmoothingStrategy.NO_SMOOTHING
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
        result[(cov, base.CoverageDataSmoothingStrategy.NO_SMOOTHING)] = df[
            cov.identifier
        ].squeeze()
        for strategy in additional_smoothing_strategies:
            df, smoothed_col = process_coverage_smoothing_strategy(
                df, cov.identifier, strategy
            )
            result[(cov, strategy)] = df[smoothed_col].squeeze()
    return result


def _get_climate_barometer_data(
    settings: config.ArpavPpcvSettings,
    coverage: coverages.CoverageInternal,
) -> pd.DataFrame:
    opendap_url = "/".join(
        (
            settings.thredds_server.base_url,
            settings.thredds_server.opendap_service_url_fragment,
            crawler.get_thredds_url_fragment(
                coverage, settings.thredds_server.base_url
            ),
        )
    )
    ds = netCDF4.Dataset(opendap_url)
    netcdf_variable_name = coverage.configuration.get_main_netcdf_variable_name(
        coverage.identifier
    )
    df = pd.DataFrame(
        {
            "time": pd.Series(
                cftime.num2pydate(
                    ds.variables["time"][:],
                    units=ds.variables["time"].units,
                    calendar=ds.variables["time"].calendar,
                )
            ),
            coverage.identifier: pd.Series(
                ds.variables[netcdf_variable_name][:].ravel(),
            ),
        }
    )
    ds.close()
    df.set_index("time", inplace=True)
    return df


def get_station_data(
    session: sqlmodel.Session,
    variable: observations.Variable,
    station: observations.Station,
    month: int,
    temporal_range: tuple[dt.datetime | None, dt.datetime | None],
) -> Optional[pd.DataFrame]:
    raw_measurements = database.collect_all_monthly_measurements(
        session=session,
        station_id_filter=station.id,
        variable_id_filter=variable.id,
        month_filter=month,
    )
    df = pd.DataFrame(m.model_dump() for m in raw_measurements)
    if not df.empty:
        df = df.rename(columns={"value": variable.name})
        df["time"] = pd.to_datetime(df["date"], utc=True)
        df = df[["time", variable.name]]
        df.set_index("time", inplace=True)
        start, end = temporal_range
        if start is not None:
            df = df[start:]
        if end is not None:
            df = df[:end]
        return df
    else:
        logger.info(
            f"Station {station.id!r} has no measurements for month {month!r} and "
            f"variable {variable.id!r}"
        )


def aggregate_decade_data(
    variable: observations.Variable, measurements: pd.DataFrame
) -> pd.DataFrame:
    # group values by climatological decade, which starts at year 1 and ends at year 10
    decade_grouper = measurements.groupby(((measurements.index.year - 1) // 10) * 10)

    mean_column_name = variable.name
    decade_df = decade_grouper.agg(
        num_values=(variable.name, "size"),
        **{mean_column_name: (variable.name, "mean")},
    )
    # discard decades where there are less than 7 years
    decade_df = decade_df[decade_df.num_values >= 7]
    decade_df = decade_df.drop(columns=["num_values"])
    decade_df["time"] = pd.to_datetime(decade_df.index.astype(str), utc=True)
    decade_df.set_index("time", inplace=True)
    return decade_df


def generate_mann_kendall_data(
    variable: observations.Variable,
    measurements: pd.DataFrame,
    parameters: base.MannKendallParameters,
) -> tuple[pd.DataFrame, dict[str, str | int | float]]:
    mk_col = f"{variable.name}__MANN_KENDALL"
    mk_start = parameters.start_year or measurements.index[0].year
    mk_end = parameters.end_year or measurements.index[-1].year
    if mk_end - mk_start >= 27:
        mk_df = measurements[str(mk_start) : str(mk_end)].copy()
        mk_result = mk.original_test(mk_df[variable.name])
        mk_df[mk_col] = (
            mk_result.slope * (mk_df.index.year - mk_df.index.year.min())
            + mk_result.intercept
        )
        # mk_df = mk_df[["time", mk_col]].rename(columns={mk_col: variable.name})
        mk_df = mk_df[[mk_col]].rename(columns={mk_col: variable.name})
        info = {
            "trend": mk_result.trend,
            "h": bool(mk_result.h),
            "p": mk_result.p,
            "z": mk_result.z,
            "tau": mk_result.Tau,
            "s": mk_result.s,
            "var_s": mk_result.var_s,
            "slope": mk_result.slope,
            "intercept": mk_result.intercept,
        }
        return mk_df, info
    else:
        raise ValueError("Mann-Kendall start and end year must span at least 27 years")


def get_observation_time_series(
    session: sqlmodel.Session,
    variable: observations.Variable,
    station: observations.Station,
    month: int,
    temporal_range: str,
    smoothing_strategies: list[base.ObservationDataSmoothingStrategy] = [  # noqa
        base.ObservationDataSmoothingStrategy.NO_SMOOTHING
    ],
    include_decade_data: bool = False,
    mann_kendall_parameters: base.MannKendallParameters | None = None,
) -> dict[
    tuple[
        base.ObservationDataSmoothingStrategy, Optional[base.ObservationDerivedSeries]
    ],
    tuple[pd.Series, Optional[dict]],
]:
    """Get monthly observation measurements."""
    start, end = parse_temporal_range(temporal_range)
    df = get_station_data(session, variable, station, month, (start, end))
    if df is not None:
        result = {
            (base.ObservationDataSmoothingStrategy.NO_SMOOTHING, None): (
                df[variable.name].squeeze(),
                None,
            )
        }
        additional_strategies = [
            ss
            for ss in smoothing_strategies
            if ss != base.ObservationDataSmoothingStrategy.NO_SMOOTHING
        ]
        for smoothing_strategy in additional_strategies:
            smoothed_df, smoothed_column_name = process_station_data_smoothing_strategy(
                df, variable.name, smoothing_strategy
            )
            result[(smoothing_strategy, None)] = (
                smoothed_df[smoothed_column_name].squeeze(),
                None,
            )
        if include_decade_data:
            decade_df = aggregate_decade_data(variable, df)
            result[
                (
                    base.ObservationDataSmoothingStrategy.NO_SMOOTHING,
                    base.ObservationDerivedSeries.DECADE_SERIES,
                )
            ] = (decade_df[variable.name].squeeze(), None)
        if mann_kendall_parameters is not None:
            mk_df, mk_info = generate_mann_kendall_data(
                variable, df, mann_kendall_parameters
            )
            result[
                (
                    base.ObservationDataSmoothingStrategy.NO_SMOOTHING,
                    base.ObservationDerivedSeries.MANN_KENDALL_SERIES,
                )
            ] = (mk_df[variable.name].squeeze(), {"mann-kendall": mk_info})
        return result


def old_get_observation_time_series(
    session: sqlmodel.Session,
    variable: observations.Variable,
    station: observations.Station,
    month: int,
    temporal_range: str,
    smoothing_strategies: list[base.ObservationDataSmoothingStrategy] = [  # noqa
        base.ObservationDataSmoothingStrategy.NO_SMOOTHING
    ],
    include_decade_data: bool = False,
    mann_kendall_parameters: base.MannKendallParameters | None = None,
) -> tuple[
    pd.DataFrame,
    Optional[pd.DataFrame],
    Optional[pd.DataFrame],
    Optional[dict[str, str]],
]:
    start, end = parse_temporal_range(temporal_range)
    raw_measurements = database.collect_all_monthly_measurements(
        session=session,
        station_id_filter=station.id,
        variable_id_filter=variable.id,
        month_filter=month,
    )
    df = pd.DataFrame(m.model_dump() for m in raw_measurements)
    base_name = variable.name
    df = df[["value", "date"]].rename(columns={"value": base_name})
    df["time"] = pd.to_datetime(df["date"], utc=True)
    df = df[["time", base_name]]
    df.set_index("time", inplace=True)
    if start is not None:
        df = df[start:]
    if end is not None:
        df = df[:end]
    unsmoothed_col_name = "__".join(
        (base_name, base.ObservationDataSmoothingStrategy.NO_SMOOTHING.value)
    )
    df[unsmoothed_col_name] = df[base_name]
    info = {}

    if include_decade_data:
        # group values by climatological decade, which starts at year 1 and ends at year 10
        decade_grouper = df.groupby(((df.index.year - 1) // 10) * 10)

        mean_column_name = f"{base_name}__DECADE_MEAN"
        decade_df = decade_grouper.agg(
            num_values=(unsmoothed_col_name, "size"),
            **{mean_column_name: (unsmoothed_col_name, "mean")},
        )

        # discard decades where there are less than 7 years
        decade_df = decade_df[decade_df.num_values >= 7]

        decade_df = decade_df.drop(columns=["num_values"])
        decade_df["time"] = pd.to_datetime(decade_df.index.astype(str), utc=True)
        decade_df.set_index("time", inplace=True)
    else:
        decade_df = None

    if mann_kendall_parameters is not None:
        mk_col = f"{base_name}__MANN_KENDALL"
        mk_start = mann_kendall_parameters.start_year or df.index[0].year
        mk_end = mann_kendall_parameters.end_year or df.index[-1].year
        if mk_end - mk_start >= 27:
            mk_df = df[str(mk_start) : str(mk_end)].copy()
            mk_result = mk.original_test(mk_df[base_name])
            mk_df[mk_col] = (
                mk_result.slope * (mk_df.index.year - mk_df.index.year.min())
                + mk_result.intercept
            )
            mk_df = mk_df.drop(columns=[base_name, unsmoothed_col_name])
            info.update(
                {
                    "mann_kendall": {
                        "trend": mk_result.trend,
                        "h": mk_result.h,
                        "p": mk_result.p,
                        "z": mk_result.z,
                        "tau": mk_result.Tau,
                        "s": mk_result.s,
                        "var_s": mk_result.var_s,
                        "slope": mk_result.slope,
                        "intercept": mk_result.intercept,
                    }
                }
            )
        else:
            raise ValueError(
                "Mann-Kendall start and end year must span at least 27 years"
            )
    else:
        mk_df = None

    for smoothing_strategy in smoothing_strategies:
        if (
            smoothing_strategy
            == base.ObservationDataSmoothingStrategy.MOVING_AVERAGE_5_YEARS
        ):
            col_name = "__".join((base_name, smoothing_strategy.value))
            df[col_name] = df[base_name].rolling(window=5, center=True).mean()

    df = df.drop(
        columns=[
            base_name,
        ]
    )
    return df, decade_df, mk_df, info if len(info) > 0 else None


async def async_retrieve_data_via_ncss(
    settings: config.ArpavPpcvSettings,
    coverage: coverages.CoverageInternal,
    point_geom: shapely.geometry.Point,
    temporal_range: tuple[dt.datetime | None, dt.datetime | None],
    http_client: httpx.AsyncClient,
    result_gatherer: dict,
) -> None:
    time_start, time_end = temporal_range
    ds_fragment = crawler.get_thredds_url_fragment(
        coverage, settings.thredds_server.base_url
    )
    ncss_url = "/".join(
        (
            settings.thredds_server.base_url,
            settings.thredds_server.netcdf_subset_service_url_fragment,
            ds_fragment,
        )
    )
    raw_coverage_data = await ncss.async_query_dataset(
        http_client,
        thredds_ncss_url=ncss_url,
        netcdf_variable_name=coverage.configuration.get_main_netcdf_variable_name(
            coverage.identifier
        ),
        longitude=point_geom.x,
        latitude=point_geom.y,
        time_start=time_start,
        time_end=time_end,
    )
    result_gatherer[coverage] = raw_coverage_data


async def retrieve_multiple_ncss_datasets(
    settings: config.ArpavPpcvSettings,
    client: httpx.AsyncClient,
    datasets_to_retrieve: list[coverages.CoverageInternal],
    point_geom: shapely.Point,
    temporal_range: tuple[dt.datetime | None, dt.datetime | None],
):
    raw_data = {}
    async with anyio.create_task_group() as tg:
        for to_retrieve in datasets_to_retrieve:
            tg.start_soon(
                async_retrieve_data_via_ncss,
                settings,
                to_retrieve,
                point_geom,
                temporal_range,
                client,
                raw_data,
            )
    return raw_data


def _parse_ncss_dataset(
    raw_data: str,
    source_main_ds_name: str,
    time_start: dt.datetime | None,
    time_end: dt.datetime | None,
    target_main_ds_name: str | None = None,
) -> pd.DataFrame:
    df = pd.read_csv(io.StringIO(raw_data), parse_dates=["time"])
    try:
        col_name = [c for c in df.columns if c.startswith(f"{source_main_ds_name}[")][0]
    except IndexError:
        raise RuntimeError(
            f"Could not extract main data series from dataframe "
            f"with columns {df.columns}"
        )
    else:
        # keep only time and main variable - we don't care about other stuff
        df = df[["time", col_name]]
        if target_main_ds_name is not None:
            df = df.rename(columns={col_name: target_main_ds_name})

        # - filter out values outside the temporal range
        df.set_index("time", inplace=True)

        # check that we got a datetime index, otherwise we need to modify the values
        if type(df.index) is not DatetimeIndex:
            new_index = pd.to_datetime(df.index.map(_simplify_date))
            df.index = new_index

        if time_start is not None:
            df = df[time_start:]
        if time_end is not None:
            df = df[:time_end]
        return df


def _simplify_date(raw_date: str) -> str:
    """Simplify a date by loosing its day and time information.

    This will reset a date to the 15th day of the underlying month.
    """
    raw_year, raw_month = raw_date.split("-")[:2]
    return f"{raw_year}-{raw_month}-15T00:00:00+00:00"


def process_coverage_smoothing_strategy(
    df: pd.DataFrame,
    column_to_smooth: str,
    strategy: base.CoverageDataSmoothingStrategy,
    ignore_warnings: bool = True,
) -> tuple[pd.DataFrame, str]:
    smoothed_column_name = "__".join((column_to_smooth, strategy.value))
    if strategy == base.CoverageDataSmoothingStrategy.LOESS_SMOOTHING:
        df[smoothed_column_name] = _apply_loess_smoothing(
            df, column_to_smooth, ignore_warnings=ignore_warnings
        )
    elif strategy == base.CoverageDataSmoothingStrategy.MOVING_AVERAGE_11_YEARS:
        df[smoothed_column_name] = (
            df[column_to_smooth].rolling(center=True, window=11).mean()
        )
    else:
        raise NotImplementedError(f"smoothing strategy {strategy!r} is not implemented")
    return df, smoothed_column_name


def process_station_data_smoothing_strategy(
    df: pd.DataFrame,
    column_to_smooth: str,
    strategy: base.ObservationDataSmoothingStrategy,
) -> tuple[pd.DataFrame, str]:
    smoothed_column_name = "__".join((column_to_smooth, strategy.value))
    if strategy == base.ObservationDataSmoothingStrategy.MOVING_AVERAGE_5_YEARS:
        df[smoothed_column_name] = (
            df[column_to_smooth].rolling(window=5, center=True).mean()
        )
    else:
        raise NotImplementedError(f"smoothing strategy {strategy!r} is not implemented")
    return df, smoothed_column_name


def get_related_uncertainty_coverage_configurations(
    session: sqlmodel.Session,
    coverage: coverages.CoverageInternal,
) -> tuple[coverages.CoverageInternal | None, coverages.CoverageInternal | None]:
    used_values = [
        pv.configuration_parameter_value
        for pv in coverage.configuration.retrieve_used_values(coverage.identifier)
    ]
    lower_, upper_ = database.ensure_uncertainty_type_configuration_parameters_exist(
        session
    )
    if (
        lower_cov_conf
        := coverage.configuration.uncertainty_lower_bounds_coverage_configuration
    ):
        lower_cov_id = lower_cov_conf.build_coverage_identifier(used_values + [lower_])
        lower_cov = coverages.CoverageInternal(
            configuration=lower_cov_conf, identifier=lower_cov_id
        )
    else:
        lower_cov = None
    if (
        upper_cov_conf
        := coverage.configuration.uncertainty_upper_bounds_coverage_configuration
    ):
        upper_cov_id = upper_cov_conf.build_coverage_identifier(used_values + [upper_])
        upper_cov = coverages.CoverageInternal(
            configuration=upper_cov_conf, identifier=upper_cov_id
        )
    else:
        upper_cov = None
    return lower_cov, upper_cov


def get_related_coverages(
    coverage: coverages.CoverageInternal,
) -> list[coverages.CoverageInternal]:
    related_covs = []
    used_values = coverage.configuration.retrieve_used_values(coverage.identifier)
    for related_ in coverage.configuration.secondary_coverage_configurations:
        related_cov_conf = related_.secondary_coverage_configuration
        possible_used = [
            pv.configuration_parameter_value for pv in related_cov_conf.possible_values
        ]
        possible_used_ids = [
            (
                uv.configuration_parameter.id,
                uv.id,
            )
            for uv in possible_used
        ]
        values_to_use = []
        for used_value in used_values:
            used_value_ids = (
                used_value.configuration_parameter_value.configuration_parameter_id,
                used_value.configuration_parameter_value.id,
            )
            if used_value_ids in possible_used_ids:
                values_to_use.append(used_value.configuration_parameter_value)
            else:
                used_param_id = (
                    used_value.configuration_parameter_value.configuration_parameter_id
                )
                try:
                    first_used_value_with_same_config_parameter = [
                        cp
                        for cp in possible_used
                        if cp.configuration_parameter_id == used_param_id
                    ][0]
                    values_to_use.append(first_used_value_with_same_config_parameter)
                except IndexError:
                    logger.warning(f"Could not find a usable value for {used_value}")
        related_id = related_cov_conf.build_coverage_identifier(values_to_use)
        related_covs.append(
            coverages.CoverageInternal(
                configuration=related_cov_conf, identifier=related_id
            )
        )
    return related_covs


def get_coverage_time_series(
    settings: config.ArpavPpcvSettings,
    session: sqlmodel.Session,
    http_client: httpx.AsyncClient,
    coverage: coverages.CoverageInternal,
    point_geom: shapely.Point,
    temporal_range: str,
    coverage_smoothing_strategies: list[base.CoverageDataSmoothingStrategy],
    observation_smoothing_strategies: list[base.ObservationDataSmoothingStrategy],
    include_coverage_data: bool = True,
    include_observation_data: bool = False,
    include_coverage_uncertainty: bool = False,
    include_coverage_related_data: bool = False,
) -> tuple[
    dict[
        tuple[coverages.CoverageInternal, base.CoverageDataSmoothingStrategy], pd.Series
    ],
    Optional[
        dict[
            tuple[
                observations.Station,
                observations.Variable,
                base.ObservationDataSmoothingStrategy,
            ],
            pd.Series,
        ]
    ],
]:
    start, end = parse_temporal_range(temporal_range)
    to_retrieve_from_ncss = [coverage]
    if include_coverage_uncertainty:
        lower_cov, upper_cov = get_related_uncertainty_coverage_configurations(
            session, coverage
        )
        if lower_cov is not None:
            to_retrieve_from_ncss.append(lower_cov)
        if upper_cov is not None:
            to_retrieve_from_ncss.append(upper_cov)
    if include_coverage_related_data:
        related_covs = get_related_coverages(coverage)
        to_retrieve_from_ncss.extend(related_covs)
    with start_blocking_portal() as portal:
        raw_data = portal.call(
            retrieve_multiple_ncss_datasets,
            settings,
            http_client,
            to_retrieve_from_ncss,
            point_geom,
            (start, end),
        )
    coverage_result = {}
    additional_coverage_smoothing_strategies = [
        ss
        for ss in coverage_smoothing_strategies
        if ss != base.CoverageDataSmoothingStrategy.NO_SMOOTHING
    ]

    for cov, data_ in raw_data.items():
        cov: coverages.CoverageInternal
        df = _parse_ncss_dataset(
            data_,
            cov.configuration.get_main_netcdf_variable_name(cov.identifier),
            start,
            end,
            cov.identifier,
        )
        unsmoothed_data = df[cov.identifier]
        coverage_result[
            (cov, base.CoverageDataSmoothingStrategy.NO_SMOOTHING)
        ] = unsmoothed_data
        if unsmoothed_data.count() > 1:
            for smoothing_strategy in additional_coverage_smoothing_strategies:
                df, smoothed_column = process_coverage_smoothing_strategy(
                    df,
                    cov.identifier,
                    smoothing_strategy,
                    ignore_warnings=(not settings.debug),
                )
                coverage_result[(cov, smoothing_strategy)] = df[
                    smoothed_column
                ].squeeze()

    if not include_coverage_data:
        del coverage_result[(coverage, base.CoverageDataSmoothingStrategy.NO_SMOOTHING)]
        for smoothing_strategy in additional_coverage_smoothing_strategies:
            try:
                del coverage_result[(coverage, smoothing_strategy)]
            except (
                KeyError
            ):  # requested smoothing may not be present if the data has a single row
                pass

    observation_result = None
    if include_observation_data:
        additional_observation_smoothing_strategies = [
            ss
            for ss in observation_smoothing_strategies
            if ss != base.ObservationDataSmoothingStrategy.NO_SMOOTHING
        ]
        variable = coverage.configuration.related_observation_variable
        if coverage.configuration.related_observation_variable is not None:
            station_data = extract_nearby_station_data(
                session,
                settings,
                point_geom,
                coverage.configuration,
                coverage.identifier,
            )
            if station_data is not None:
                observation_result = {}
                raw_station_data, station = station_data
                station_df = _process_station_data(
                    raw_station_data,
                    start,
                    end,
                    variable.name,
                    aggregation_type=(
                        coverage.configuration.observation_variable_aggregation_type
                    ),
                )
                observation_result[
                    (
                        station,
                        variable,
                        base.ObservationDataSmoothingStrategy.NO_SMOOTHING,
                    )
                ] = station_df[variable.name].squeeze()
                for smoothing_strategy in additional_observation_smoothing_strategies:
                    (
                        station_df,
                        smoothed_column,
                    ) = process_station_data_smoothing_strategy(
                        station_df, variable.name, smoothing_strategy
                    )
                    observation_result[
                        (station, variable, smoothing_strategy)
                    ] = station_df[smoothed_column].squeeze()
            else:
                logger.info("No station data found, skipping...")
        else:
            logger.info(
                "Cannot include observation data - no observation variable is related "
                "to this coverage configuration"
            )
    return coverage_result, observation_result


def extract_nearby_station_data(
    session: sqlmodel.Session,
    settings: config.ArpavPpcvSettings,
    point_geom: shapely.Point,
    coverage_configuration: coverages.CoverageConfiguration,
    coverage_identifier: str,
) -> Optional[
    tuple[
        list[
            observations.MonthlyMeasurement
            | observations.SeasonalMeasurement
            | observations.YearlyMeasurement
        ],
        observations.Station,
    ]
]:
    point_buffer_geom = _get_spatial_buffer(
        point_geom, settings.nearest_station_radius_meters
    )
    nearby_stations = database.collect_all_stations(
        session, polygon_intersection_filter=point_buffer_geom
    )
    if len(nearby_stations) > 0:
        retriever_kwargs = {
            "variable_id_filter": coverage_configuration.observation_variable_id
        }
        aggregation_type = coverage_configuration.observation_variable_aggregation_type
        if aggregation_type == base.ObservationAggregationType.MONTHLY:
            retriever = functools.partial(
                database.collect_all_monthly_measurements,
                session,
                **retriever_kwargs,
                month_filter=None,
            )
        elif aggregation_type == base.ObservationAggregationType.SEASONAL:
            retriever = functools.partial(
                database.collect_all_seasonal_measurements,
                session,
                **retriever_kwargs,
                season_filter=coverage_configuration.get_seasonal_aggregation_query_filter(
                    coverage_identifier
                ),
            )
        else:  # ANNUAL
            retriever = functools.partial(
                database.collect_all_yearly_measurements,
                session,
                **retriever_kwargs,
            )
        sorted_stations = sorted(
            nearby_stations, key=lambda s: to_shape(s.geom).distance(point_geom)
        )
        # order nearby stations by distance and then iterate through them in order to
        # try to get measurements for the relevant variable and temporal aggregation
        for station in sorted_stations:
            logger.debug(f"Processing station {station.id}...")
            raw_station_data = retriever(station_id_filter=station.id)
            if len(raw_station_data) > 0:
                # stop with the first station that has data
                result = (raw_station_data, station)
                break
        else:
            result = None
            logger.info("Nearby stations do not have data")
    else:
        logger.info(
            f"There are no nearby stations from {shapely.io.to_wkt(point_geom)}"
        )
        result = None
    return result


def _process_station_data(
    raw_data: list[observations.SeasonalMeasurement],
    time_start: Optional[dt.datetime],
    time_end: Optional[dt.datetime],
    base_name: str,
    aggregation_type: base.ObservationAggregationType,
):
    df = pd.DataFrame([i.model_dump() for i in raw_data])
    df = df.rename(columns={"value": base_name})
    if aggregation_type == base.ObservationAggregationType.SEASONAL:
        df["season_month"] = (
            df["season"]
            .astype("string")
            .replace(
                {
                    "Season.WINTER": "01",
                    "Season.SPRING": "04",
                    "Season.SUMMER": "07",
                    "Season.AUTUMN": "10",
                }
            )
        )
        df["time"] = pd.to_datetime(
            df["year"].astype("string") + "-" + df["season_month"] + "-01", utc=True
        )
    elif aggregation_type == base.ObservationAggregationType.YEARLY:
        df["time"] = pd.to_datetime(df["year"].astype("string"), utc=True)
    else:
        raise RuntimeError(
            f"Unable to process station data with aggregation type {aggregation_type}"
        )

    df = df[[base_name, "time"]]
    df.set_index("time", inplace=True)
    if time_start is not None:
        df = df[time_start:]
    if time_end is not None:
        df = df[:time_end]
    return df


def _apply_loess_smoothing(
    df: pd.DataFrame, source_column_name: str, ignore_warnings: bool = True
) -> np.ndarray:
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


def parse_temporal_range(
    raw_temporal_range: str,
) -> tuple[dt.datetime | None, dt.datetime | None]:
    """Parse a temporal range string, converting time to UTC.

    The expected format for the input temporal range is described in the
    OGC API - EDR standard:

    https://docs.ogc.org/is/19-086r6/19-086r6.html#req_core_rc-time-response

    Basically it is a string with an optional start datetime and an optional end
    datetime.
    """

    raw_start, raw_end = raw_temporal_range.partition("/")[::2]
    open_interval_pattern = ".."
    if raw_start != open_interval_pattern:
        start = isoparse(raw_start).astimezone(dt.timezone.utc)
    else:
        start = None
    if raw_end != open_interval_pattern:
        end = isoparse(raw_end).astimezone(dt.timezone.utc)
    else:
        end = None
    return start, end


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


def get_historical_variable_parameters(
    session: sqlmodel.Session,
) -> dict[str, coverages.HistoricalVariableMenuTree]:
    result = {}
    historical_filter = database.get_configuration_parameter_value_by_names(
        session, base.CoreConfParamName.ARCHIVE.value, "historical"
    )
    relevant_cov_confs = database.collect_all_coverage_configurations(
        session, configuration_parameter_values_filter=[historical_filter]
    )
    for cov_conf in relevant_cov_confs:
        variable_pvs = [
            pv
            for pv in cov_conf.possible_values
            if pv.configuration_parameter_value.configuration_parameter.name
            == base.CoreConfParamName.HISTORICAL_VARIABLE.value
        ]
        if (num_pvs := len(variable_pvs)) >= 1:
            variable_pv = variable_pvs[0]
            if num_pvs > 1:
                logger.info(
                    f"coverage configuration {cov_conf.name!r} defines "
                    f"{len(variable_pvs)} `historical_variable`s, keeping only the "
                    f"first one..."
                )
        else:
            logger.info(
                f"coverage configuration {cov_conf.name!r} does not have a "
                f"`historical_variable`, skipping..."
            )
            continue
        aggreg_period_pvs = [
            pv
            for pv in cov_conf.possible_values
            if pv.configuration_parameter_value.configuration_parameter.name
            == base.CoreConfParamName.AGGREGATION_PERIOD.value
        ]
        if (num_aggreg_periods := len(aggreg_period_pvs)) >= 1:
            aggreg_period_pv = aggreg_period_pvs[0]
            if num_aggreg_periods > 1:
                logger.info(
                    f"coverage configuration {cov_conf.name!r} defines "
                    f"{len(variable_pvs)} `aggregation_period`s, keeping only the "
                    f"first one..."
                )
        else:
            logger.info(
                f"coverage configuration {cov_conf.name!r} does not have a "
                f"`aggregation_period`, skipping..."
            )
            continue
        result_key = "-".join(
            (
                variable_pv.configuration_parameter_value.name,
                aggreg_period_pv.configuration_parameter_value.name,
            )
        )
        aggregated_variable = result.setdefault(result_key, {})
        aggregated_variable[
            base.CoreConfParamName.HISTORICAL_VARIABLE.value
        ] = variable_pv.configuration_parameter_value
        aggregated_variable[
            base.CoreConfParamName.AGGREGATION_PERIOD.value
        ] = aggreg_period_pv.configuration_parameter_value
        combinations = aggregated_variable.setdefault("combinations", {})
        params_to_ignore = (
            base.CoreConfParamName.CLIMATOLOGICAL_VARIABLE.value,
            base.CoreConfParamName.AGGREGATION_PERIOD.value,
            base.CoreConfParamName.UNCERTAINTY_TYPE.value,
        )
        for pv in cov_conf.possible_values:
            param_name = pv.configuration_parameter_value.configuration_parameter.name
            if param_name not in params_to_ignore:
                param_entry = combinations.setdefault(param_name, {})
                param_entry[
                    "configuration_parameter"
                ] = pv.configuration_parameter_value.configuration_parameter
                values = param_entry.setdefault("values", [])
                existing_value_names = [cpv.name for cpv in values]
                if pv.configuration_parameter_value.name not in existing_value_names:
                    values.append(pv.configuration_parameter_value)
    return result


def get_forecast_variable_parameters(
    session: sqlmodel.Session,
) -> dict[str, coverages.ForecastVariableMenuTree]:
    result = {}
    forecast_filter = database.get_configuration_parameter_value_by_names(
        session, base.CoreConfParamName.ARCHIVE.value, "forecast"
    )
    relevant_cov_confs = database.collect_all_coverage_configurations(
        session, configuration_parameter_values_filter=[forecast_filter]
    )
    for cov_conf in relevant_cov_confs:
        variable_pvs = [
            pv
            for pv in cov_conf.possible_values
            if pv.configuration_parameter_value.configuration_parameter.name
            == base.CoreConfParamName.CLIMATOLOGICAL_VARIABLE.value
        ]
        if (num_pvs := len(variable_pvs)) >= 1:
            variable_pv = variable_pvs[0]
            if num_pvs > 1:
                logger.info(
                    f"coverage configuration {cov_conf.name!r} defines "
                    f"{len(variable_pvs)} `climatological_variable`s, keeping only the "
                    f"first one..."
                )
        else:
            logger.info(
                f"coverage configuration {cov_conf.name!r} does not have a "
                f"`climatological_variable`, skipping..."
            )
            continue

        aggreg_period_pvs = [
            pv
            for pv in cov_conf.possible_values
            if pv.configuration_parameter_value.configuration_parameter.name
            == base.CoreConfParamName.AGGREGATION_PERIOD.value
        ]
        if (num_aggreg_periods := len(aggreg_period_pvs)) >= 1:
            aggreg_period_pv = aggreg_period_pvs[0]
            if num_aggreg_periods > 1:
                logger.info(
                    f"coverage configuration {cov_conf.name!r} defines "
                    f"{len(variable_pvs)} `aggregation_period`s, keeping only the "
                    f"first one..."
                )
        else:
            logger.info(
                f"coverage configuration {cov_conf.name!r} does not have a "
                f"`aggregation_period`, skipping..."
            )
            continue

        measure_pvs = [
            pv
            for pv in cov_conf.possible_values
            if pv.configuration_parameter_value.configuration_parameter.name
            == base.CoreConfParamName.MEASURE.value
        ]
        if (num_measures := len(measure_pvs)) >= 1:
            measure_pv = measure_pvs[0]
            if num_measures > 1:
                logger.info(
                    f"coverage configuration {cov_conf.name!r} defines "
                    f"{len(variable_pvs)} `measures`s, keeping only the "
                    f"first one..."
                )
        else:
            logger.info(
                f"coverage configuration {cov_conf.name!r} does not have a "
                f"`measure`, skipping..."
            )
            continue

        result_key = "-".join(
            (
                variable_pv.configuration_parameter_value.name,
                aggreg_period_pv.configuration_parameter_value.name,
                measure_pv.configuration_parameter_value.name,
            )
        )
        aggregated_variable = result.setdefault(result_key, {})
        aggregated_variable[
            base.CoreConfParamName.CLIMATOLOGICAL_VARIABLE.value
        ] = variable_pv.configuration_parameter_value
        aggregated_variable[
            base.CoreConfParamName.AGGREGATION_PERIOD.value
        ] = aggreg_period_pv.configuration_parameter_value
        aggregated_variable[
            base.CoreConfParamName.MEASURE.value
        ] = measure_pv.configuration_parameter_value
        combinations = aggregated_variable.setdefault("combinations", {})
        params_to_ignore = (
            base.CoreConfParamName.CLIMATOLOGICAL_VARIABLE.value,
            base.CoreConfParamName.AGGREGATION_PERIOD.value,
            base.CoreConfParamName.MEASURE.value,
            base.CoreConfParamName.UNCERTAINTY_TYPE.value,
        )
        for pv in cov_conf.possible_values:
            param_name = pv.configuration_parameter_value.configuration_parameter.name
            if param_name not in params_to_ignore:
                param_entry = combinations.setdefault(param_name, {})
                param_entry[
                    "configuration_parameter"
                ] = pv.configuration_parameter_value.configuration_parameter
                values = param_entry.setdefault("values", [])
                existing_value_names = [cpv.name for cpv in values]
                if pv.configuration_parameter_value.name not in existing_value_names:
                    values.append(pv.configuration_parameter_value)
    return result


def create_db_schema(session: sqlmodel.Session, schema_name: str):
    session.execute(sqlmodel.text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
    session.commit()


def refresh_station_variable_database_view(
    session: sqlmodel.Session,
    variable: observations.Variable,
    db_schema_name: Optional[str] = "public",
):
    sanitized_name = sanitize_observation_variable_name(variable.name)
    view_name = f"{db_schema_name}.stations_{sanitized_name}"
    index_name = f"idx_{sanitized_name}"
    drop_view_statement = sqlmodel.text(f"DROP MATERIALIZED VIEW IF EXISTS {view_name}")
    create_view_statement = sqlmodel.text(
        f"CREATE MATERIALIZED VIEW {view_name} "
        f"AS SELECT DISTINCT s.* "
        f"FROM yearlymeasurement AS ym "
        f"JOIN station AS s ON s.id = ym.station_id "
        f"JOIN variable AS v ON v.id = ym.variable_id "
        f"WHERE v.name = '{variable.name}' "
        f"UNION "
        f"SELECT DISTINCT s.* "
        f"FROM seasonalmeasurement AS sm "
        f"JOIN station AS s ON s.id = sm.station_id "
        f"JOIN variable AS v ON v.id = sm.variable_id "
        f"WHERE v.name = '{variable.name}' "
        f"UNION "
        f"SELECT DISTINCT s.* "
        f"FROM monthlymeasurement AS mm "
        f"JOIN station AS s ON s.id = mm.station_id "
        f"JOIN variable AS v ON v.id = mm.variable_id "
        f"WHERE v.name = '{variable.name}' "
        f"WITH DATA"
    )
    drop_index_statement = sqlmodel.text(f"DROP INDEX IF EXISTS {index_name}")
    create_index_statement = sqlmodel.text(
        f"CREATE INDEX {index_name} ON {view_name} USING gist (geom)"
    )
    session.execute(drop_view_statement)
    session.execute(drop_index_statement)
    session.execute(create_view_statement)
    session.execute(create_index_statement)
    session.commit()


def sanitize_observation_variable_name(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_")
