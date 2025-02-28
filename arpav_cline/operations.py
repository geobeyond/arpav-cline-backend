import datetime as dt
import logging
from typing import (
    Optional,
    Sequence,
    TYPE_CHECKING,
)

import pandas as pd
import pymannkendall as mk
import sqlmodel

from dateutil.parser import isoparse

from . import db
from .schemas import (
    base,
    coverages,
    legacy,
    static,
)

if TYPE_CHECKING:
    from .schemas.climaticindicators import ClimaticIndicator

logger = logging.getLogger(__name__)


def aggregate_decade_data(
    climatic_indicator: "ClimaticIndicator", measurements: pd.DataFrame
) -> pd.DataFrame:
    # group values by climatological decade, which starts at year 1 and ends at year 10
    decade_grouper = measurements.groupby(((measurements.index.year - 1) // 10) * 10)

    mean_column_name = climatic_indicator.name
    decade_df = decade_grouper.agg(
        num_values=(climatic_indicator.name, "size"),
        **{mean_column_name: (climatic_indicator.name, "mean")},
    )
    # discard decades where there are less than 7 years
    decade_df = decade_df[decade_df.num_values >= 7]
    decade_df = decade_df.drop(columns=["num_values"])
    decade_df["time"] = pd.to_datetime(decade_df.index.astype(str), utc=True)
    decade_df.set_index("time", inplace=True)
    return decade_df


def generate_mann_kendall_data(
    climatic_indicator: "ClimaticIndicator",
    measurements: pd.DataFrame,
    parameters: base.MannKendallParameters,
) -> tuple[pd.DataFrame, dict[str, str | int | float]]:
    mk_col = f"{climatic_indicator.name}__MANN_KENDALL"
    mk_start = parameters.start_year or measurements.index[0].year
    mk_end = parameters.end_year or measurements.index[-1].year
    if mk_end - mk_start >= 27:
        mk_df = measurements[str(mk_start) : str(mk_end)].copy()
        mk_result = mk.original_test(mk_df[climatic_indicator.name])
        mk_df[mk_col] = (
            mk_result.slope * (mk_df.index.year - mk_df.index.year.min())
            + mk_result.intercept
        )
        # mk_df = mk_df[["time", mk_col]].rename(columns={mk_col: variable.name})
        mk_df = mk_df[[mk_col]].rename(columns={mk_col: climatic_indicator.name})
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


def process_station_data_smoothing_strategy(
    df: pd.DataFrame,
    column_to_smooth: str,
    strategy: static.ObservationTimeSeriesProcessingMethod,
) -> tuple[pd.DataFrame, str]:
    smoothed_column_name = "__".join((column_to_smooth, strategy.value))
    if strategy == static.ObservationTimeSeriesProcessingMethod.MOVING_AVERAGE_5_YEARS:
        df[smoothed_column_name] = (
            df[column_to_smooth].rolling(window=5, center=True).mean()
        )
    else:
        raise NotImplementedError(f"smoothing strategy {strategy!r} is not implemented")
    return df, smoothed_column_name


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


def create_db_schema(session: sqlmodel.Session, schema_name: str):
    session.execute(sqlmodel.text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
    session.commit()


def refresh_station_climatic_indicator_database_view(
    session: sqlmodel.Session,
    climatic_indicator: "ClimaticIndicator",
    db_schema_name: Optional[str] = "public",
):
    """Refresh DB view with stations that have data for input climatic indicator."""
    sanitized_name = sanitize_observation_variable_name(climatic_indicator.identifier)
    view_name = f"{db_schema_name}.stations_{sanitized_name}"
    drop_view_statement = sqlmodel.text(f"DROP MATERIALIZED VIEW IF EXISTS {view_name}")
    create_view_statement = sqlmodel.text(
        f"CREATE MATERIALIZED VIEW {view_name} "
        f"AS SELECT s.* "
        f"FROM observationstation AS s "
        f"JOIN observationstationclimaticindicatorlink AS scil ON s.id = scil.observation_station_id "
        f"JOIN climaticindicator AS ci ON ci.id = scil.climatic_indicator_id "
        f"WHERE ci.name = '{climatic_indicator.name}' "
        f"AND ci.measure_type = '{climatic_indicator.measure_type.name}' "
        f"AND ci.aggregation_period = '{climatic_indicator.aggregation_period.name}' "
        f"WITH DATA"
    )
    index_name = f"idx_{sanitized_name}"
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


def convert_conf_params_filter(
    session: sqlmodel.Session, configuration_parameter_values: Sequence[str]
) -> coverages.LegacyConfParamFilterValues:
    """Convert filter parameters from the legacy conf-param based format.

    This function converts a sequence of `name=value` strings, which was used
    in a previous version of the system to query the configuration parameters in
    use by some forecast coverage with the current approach of using well-known
    types.
    """
    aggregation_period = None
    archive = None
    climatological_model = None
    climatological_variable = None

    historical_decade = None
    historical_reference_period = None
    historical_variable = None
    historical_year_period = None

    measure = None
    scenario = None
    uncertainty_type = None
    time_window = None
    year_period = None

    climatic_indicator = None
    for raw_value in configuration_parameter_values:
        param_name, param_value = raw_value.partition(":")[::2]
        if param_name == "aggregation_period":
            aggregation_period = legacy.parse_legacy_aggregation_period(param_value)
            if aggregation_period is None:
                logger.warning(
                    f"Could not parse {param_value!r} as an aggregation period, skipping..."
                )
        elif param_name == "archive":
            archive = param_value
        elif param_name == "climatological_model":
            climatological_model = db.get_forecast_model_by_name(session, param_value)
            if climatological_model is None:
                logger.warning(
                    f"Could not parse {param_value!r} as valid forecast model name, "
                    f"skipping..."
                )
        elif param_name == "climatological_variable":
            climatological_variable = param_value
        elif param_name == historical_decade:
            try:
                historical_decade = static.HistoricalDecade(param_value)
            except ValueError:
                logger.warning(
                    f"Could not parse {param_value!r} as an historical decade, skipping..."
                )
        elif param_name == "historical_reference_period":
            try:
                historical_reference_period = static.HistoricalReferencePeriod(
                    param_value
                )
            except ValueError:
                logger.warning(
                    f"Could not parse {param_value!r} as an historical reference "
                    f"period, skipping..."
                )
        elif param_name == "historical_variable":
            historical_variable = param_value
        elif param_name == "historical_year_period":
            try:
                historical_year_period = static.HistoricalYearPeriod(param_value)
            except ValueError:
                logger.warning(
                    f"Could not parse {param_value!r} as an historical year period, skipping..."
                )
        elif param_name == "measure":
            try:
                measure = static.MeasureType(param_value)
            except ValueError:
                logger.warning(
                    f"Could not parse {param_value!r} as an measure type, skipping..."
                )
        elif param_name == "scenario":
            try:
                scenario = static.ForecastScenario(param_value)
            except ValueError:
                logger.warning(
                    f"Could not parse {param_value!r} as scenario, skipping..."
                )
        elif param_name == "time_window":
            time_window = db.get_forecast_time_window_by_name(session, param_value)
            if time_window is None:
                logger.warning(
                    f"Could not parse {param_value!r} as valid time window name, "
                    f"skipping..."
                )
        elif param_name == "year_period":
            try:
                year_period = static.ForecastYearPeriod(param_value)
            except ValueError:
                logger.warning(
                    f"Could not parse {param_value!r} as an forecast year period, skipping..."
                )
        elif param_name == "uncertainty_type":
            uncertainty_type = param_value
    if all((climatological_variable, measure, aggregation_period)):
        climatic_indicator = db.get_climatic_indicator_by_identifier(
            session,
            "-".join(
                (climatological_variable, measure.value, aggregation_period.value)
            ),
        )
    return coverages.LegacyConfParamFilterValues(
        aggregation_period=aggregation_period,
        archive=archive,
        climatic_indicator=climatic_indicator,
        climatological_variable=climatological_variable,
        climatological_model=climatological_model,
        historical_decade=historical_decade,
        historical_reference_period=historical_reference_period,
        historical_year_period=historical_year_period,
        historical_variable=historical_variable,
        measure=measure,
        scenario=scenario,
        time_window=time_window,
        year_period=year_period,
        uncertainty_type=uncertainty_type,
    )
