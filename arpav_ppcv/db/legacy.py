from typing import (
    Optional,
    Sequence,
)

import sqlalchemy
import sqlmodel

from .. import database
from ..schemas import (
    coverages,
    climaticindicators,
)
from .base import (
    add_substring_filter,
    get_total_num_records,
)


def legacy_list_forecast_coverages(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    name_filter: list[str] | None = None,
    conf_param_filter: Optional[coverages.LegacyConfParamFilterValues] = None,
) -> tuple[list[coverages.ForecastCoverageInternal], Optional[int]]:
    all_cov_confs = legacy_collect_all_forecast_coverage_configurations(
        session, conf_param_filter=conf_param_filter
    )
    result = []
    for cov_conf in all_cov_confs:
        result.extend(database.generate_forecast_coverages_from_configuration(cov_conf))
    if name_filter is not None:
        for fragment in name_filter:
            result = [fc for fc in result if fragment in fc.identifier]
    return result[offset : offset + limit], len(result) if include_total else None


def legacy_collect_all_forecast_coverage_configurations(
    session: sqlmodel.Session,
    *,
    name_filter: Optional[str] = None,
    conf_param_filter: Optional[coverages.LegacyConfParamFilterValues],
) -> Sequence[coverages.ForecastCoverageConfiguration]:
    """Collect all forecast coverage configurations.

    NOTE:

    This function supports a bunch of search filters that were previously provided by
    the more generic `configuration_parameter` instances, which were available in
    an early version of the project. This is kept only for compatibility reasons -
    newer code should use `collect_all_forecast_coverage_configurations()` instead.
    """
    _, num_total = legacy_list_forecast_coverage_configurations(
        session,
        limit=1,
        include_total=True,
        name_filter=name_filter,
        conf_param_filter=conf_param_filter,
    )
    result, _ = legacy_list_forecast_coverage_configurations(
        session,
        limit=num_total,
        include_total=False,
        name_filter=name_filter,
        conf_param_filter=conf_param_filter,
    )
    return result


def legacy_list_forecast_coverage_configurations(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    name_filter: Optional[str] = None,
    conf_param_filter: Optional[coverages.LegacyConfParamFilterValues],
):
    """List forecast coverage configurations.

    NOTE:

    This function supports a bunch of search filters that were previously provided by
    the more generic `configuration_parameter` instances, which were available in
    an early version of the project. This is kept only for compatibility reasons -
    newer code should use `list_forecast_coverage_configurations()` instead.
    """
    statement = (
        sqlmodel.select(coverages.ForecastCoverageConfiguration)
        .join(
            climaticindicators.ClimaticIndicator,
            climaticindicators.ClimaticIndicator.id
            == coverages.ForecastCoverageConfiguration.climatic_indicator_id,
        )
        .order_by(climaticindicators.ClimaticIndicator.sort_order)
    )
    if name_filter is not None:
        statement = add_substring_filter(
            statement, name_filter, climaticindicators.ClimaticIndicator.name
        )
    if conf_param_filter is not None:
        if conf_param_filter.climatic_indicator is not None:
            statement = statement.where(
                climaticindicators.ClimaticIndicator.id
                == conf_param_filter.climatic_indicator.id
            )
        else:
            if conf_param_filter.climatological_variable is not None:
                statement = statement.where(
                    climaticindicators.ClimaticIndicator.name
                    == conf_param_filter.climatological_variable
                )
            if conf_param_filter.measure is not None:
                statement = statement.where(
                    climaticindicators.ClimaticIndicator.measure_type
                    == conf_param_filter.measure.name
                )
            if conf_param_filter.aggregation_period is not None:
                statement = statement.where(
                    climaticindicators.ClimaticIndicator.aggregation_period
                    == conf_param_filter.aggregation_period.name
                )
        if conf_param_filter.climatological_model is not None:
            statement = (
                statement.join(
                    coverages.ForecastCoverageConfigurationForecastModelLink,
                    coverages.ForecastCoverageConfiguration.id
                    == coverages.ForecastCoverageConfigurationForecastModelLink.forecast_coverage_configuration_id,
                )
                .join(
                    coverages.ForecastModel,
                    coverages.ForecastModel.id
                    == coverages.ForecastCoverageConfigurationForecastModelLink.forecast_model_id,
                )
                .where(
                    coverages.ForecastModel.id
                    == conf_param_filter.climatological_model.id
                )
            )
        if conf_param_filter.scenario is not None:
            statement = statement.where(
                conf_param_filter.scenario.name
                == sqlalchemy.any_(coverages.ForecastCoverageConfiguration.scenarios)
            )
        if conf_param_filter.time_window is not None:
            statement = (
                statement.join(
                    coverages.ForecastCoverageConfigurationForecastTimeWindowLink,
                    coverages.ForecastCoverageConfiguration.id
                    == coverages.ForecastCoverageConfigurationForecastTimeWindowLink.forecast_coverage_configuration_id,
                )
                .join(
                    coverages.ForecastTimeWindow,
                    coverages.ForecastTimeWindow.id
                    == coverages.ForecastCoverageConfigurationForecastTimeWindowLink.forecast_time_window_id,
                )
                .where(
                    coverages.ForecastTimeWindow.id == conf_param_filter.time_window.id
                )
            )
        if conf_param_filter.year_period is not None:
            statement = statement.where(
                conf_param_filter.year_period.name
                == sqlalchemy.any_(coverages.ForecastCoverageConfiguration.year_periods)
            )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items
