import itertools
import logging
import uuid
from typing import (
    Final,
    Optional,
    Sequence,
)

import sqlalchemy
import sqlmodel
from sqlalchemy import func

from .. import config
from ..schemas import (
    base,
    coverages,
    climaticindicators,
    legacy as legacy_schemas,
    static,
)
from .base import (
    add_substring_filter,
    get_total_num_records,
    slugify_internal_value,
)
from .climaticindicators import (
    collect_all_climatic_indicators,
    get_climatic_indicator_by_identifier,
)
from .forecastcoverages import (
    collect_all_forecast_models,
    collect_all_forecast_time_windows,
    generate_forecast_coverages_from_configuration,
)

logger = logging.getLogger(__name__)

_FAKE_ID: Final[uuid.UUID] = uuid.UUID("06213c04-6872-4677-a149-a3b84f8da224")


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
        result.extend(generate_forecast_coverages_from_configuration(cov_conf))
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
    num_items = get_total_num_records(session, statement) if include_total else None
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


def _get_climatological_variable_conf_param(
    all_climatic_indicators: Sequence[climaticindicators.ClimaticIndicator],
):
    conf_param = coverages.ConfigurationParameter(
        id=_FAKE_ID,
        name="climatological_variable",
        display_name_english="Variable",
        display_name_italian="Variabile",
        description_english="Climatological variable",
        description_italian="Variabile climatologica",
        allowed_values=[],
    )
    seen = set()
    for indicator in all_climatic_indicators:
        if indicator.name not in seen:
            seen.add(indicator.name)
            conf_param.allowed_values.append(
                coverages.ConfigurationParameterValue(
                    id=_FAKE_ID,
                    name=indicator.name,
                    internal_value=indicator.name,
                    display_name_english=indicator.display_name_english,
                    display_name_italian=indicator.display_name_italian,
                    description_english=indicator.description_english,
                    description_italian=indicator.description_italian,
                    sort_order=indicator.sort_order,
                    configuration_parameter_id=_FAKE_ID,
                )
            )
    return conf_param


def _get_time_window_conf_param(
    session: sqlmodel.Session,
) -> coverages.ConfigurationParameter:
    conf_param = coverages.ConfigurationParameter(
        id=_FAKE_ID,
        name="time_window",
        display_name_english="Time window",
        display_name_italian="Finestra temporale",
        description_english="",
        description_italian="",
        allowed_values=[],
    )
    all_time_windows = collect_all_forecast_time_windows(session)
    seen = set()
    for time_window in all_time_windows:
        if time_window.name not in seen:
            seen.add(time_window.name)
            conf_param.allowed_values.append(
                coverages.ConfigurationParameterValue(
                    id=_FAKE_ID,
                    name=time_window.name,
                    internal_value=time_window.internal_value,
                    display_name_english=time_window.display_name_english,
                    display_name_italian=time_window.display_name_italian,
                    description_english=time_window.description_english,
                    description_italian=time_window.description_italian,
                    sort_order=time_window.sort_order,
                    configuration_parameter_id=_FAKE_ID,
                )
            )
    return conf_param


def _get_climatological_model_conf_param(
    session: sqlmodel.Session,
) -> coverages.ConfigurationParameter:
    conf_param = coverages.ConfigurationParameter(
        id=_FAKE_ID,
        name="climatological_model",
        display_name_english="Forecast model",
        display_name_italian="Modello di previsione",
        description_english=(
            "Numerical model used to generate climatological forecast datasets"
        ),
        description_italian=(
            "Modello numerico utilizzato per generare set di dati di previsione "
            "climatologica"
        ),
        allowed_values=[],
    )
    all_forecast_models = collect_all_forecast_models(session)
    seen = set()
    for forecast_model in all_forecast_models:
        if forecast_model.name not in seen:
            seen.add(forecast_model.name)
            conf_param.allowed_values.append(
                coverages.ConfigurationParameterValue(
                    id=_FAKE_ID,
                    name=forecast_model.name,
                    internal_value=forecast_model.internal_value,
                    display_name_english=forecast_model.display_name_english,
                    display_name_italian=forecast_model.display_name_italian,
                    description_english=forecast_model.description_english,
                    description_italian=forecast_model.description_italian,
                    sort_order=forecast_model.sort_order,
                    configuration_parameter_id=_FAKE_ID,
                )
            )
    return conf_param


def _get_measure_conf_param(
    all_climatic_indicators: Sequence[climaticindicators.ClimaticIndicator],
) -> coverages.ConfigurationParameter:
    conf_param = coverages.ConfigurationParameter(
        id=_FAKE_ID,
        name="measure",
        display_name_english="Measurement type",
        display_name_italian="Tipo di misurazione",
        description_english="Type of climatological measurement",
        description_italian="Tipo di misurazione climatologica",
        allowed_values=[],
    )
    seen = set()
    for indicator in all_climatic_indicators:
        if indicator.measure_type not in seen:
            seen.add(indicator.measure_type)
            conf_param.allowed_values.append(
                coverages.ConfigurationParameterValue(
                    id=_FAKE_ID,
                    name=indicator.measure_type.value,
                    internal_value=indicator.measure_type.value,
                    display_name_english=(
                        indicator.measure_type.get_value_display_name(config.LOCALE_EN)
                    ),
                    display_name_italian=(
                        indicator.measure_type.get_value_display_name(config.LOCALE_EN)
                    ),
                    description_english=(
                        indicator.measure_type.get_value_description(config.LOCALE_EN)
                    ),
                    description_italian=(
                        indicator.measure_type.get_value_description(config.LOCALE_IT)
                    ),
                    sort_order=indicator.measure_type.get_sort_order(),
                    configuration_parameter_id=_FAKE_ID,
                )
            )
    return conf_param


def _get_aggregation_period_conf_param(
    all_climatic_indicators: Sequence[climaticindicators.ClimaticIndicator],
) -> coverages.ConfigurationParameter:
    conf_param = coverages.ConfigurationParameter(
        id=_FAKE_ID,
        name="aggregation_period",
        display_name_english="Temporal aggregation period",
        display_name_italian="Periodo di aggregazione temporale",
        description_english="Aggregation period for climatological datasets",
        description_italian="Periodo di aggregazione per i set di dati climatologici",
        allowed_values=[],
    )
    seen = set()
    for indicator in all_climatic_indicators:
        if indicator.aggregation_period not in seen:
            seen.add(indicator.aggregation_period)
            converted = legacy_schemas.convert_to_aggregation_period(
                indicator.aggregation_period
            )
            conf_param.allowed_values.append(
                coverages.ConfigurationParameterValue(
                    id=_FAKE_ID,
                    name=converted,
                    internal_value=converted,
                    display_name_english=(
                        indicator.aggregation_period.get_value_display_name(
                            config.LOCALE_EN
                        )
                    ),
                    display_name_italian=(
                        indicator.aggregation_period.get_value_display_name(
                            config.LOCALE_EN
                        )
                    ),
                    description_english=(
                        indicator.aggregation_period.get_value_description(
                            config.LOCALE_EN
                        )
                    ),
                    description_italian=(
                        indicator.aggregation_period.get_value_description(
                            config.LOCALE_IT
                        )
                    ),
                    sort_order=indicator.aggregation_period.get_sort_order(),
                    configuration_parameter_id=_FAKE_ID,
                )
            )
    return conf_param


def _get_scenario_conf_param() -> coverages.ConfigurationParameter:
    conf_param = coverages.ConfigurationParameter(
        id=_FAKE_ID,
        name="scenario",
        display_name_english="Scenario",
        display_name_italian="Scenario",
        description_english="Climate model scenario",
        description_italian="Scenario del modello climatico",
        allowed_values=[],
    )
    for scenario in static.ForecastScenario.__members__.values():
        conf_param.allowed_values.append(
            coverages.ConfigurationParameterValue(
                id=_FAKE_ID,
                name=scenario.value,
                internal_value=scenario.value,
                display_name_english=scenario.get_value_display_name(config.LOCALE_EN),
                display_name_italian=scenario.get_value_display_name(config.LOCALE_EN),
                description_english=scenario.get_value_description(config.LOCALE_EN),
                description_italian=scenario.get_value_description(config.LOCALE_IT),
                sort_order=scenario.get_sort_order(),
                configuration_parameter_id=_FAKE_ID,
            )
        )
    return conf_param


def _get_year_period_conf_param() -> coverages.ConfigurationParameter:
    conf_param = coverages.ConfigurationParameter(
        id=_FAKE_ID,
        name="year_period",
        display_name_italian="Periodo dell'anno",
        description_english="Yearly temporal aggregation period",
        description_italian="Periodo di aggregazione temporale annuale",
        allowed_values=[],
    )
    for year_period in static.ForecastYearPeriod.__members__.values():
        conf_param.allowed_values.append(
            coverages.ConfigurationParameterValue(
                id=_FAKE_ID,
                name=year_period.value,
                internal_value=year_period.value,
                display_name_english=year_period.get_value_display_name(
                    config.LOCALE_EN
                ),
                display_name_italian=year_period.get_value_display_name(
                    config.LOCALE_EN
                ),
                description_english=year_period.get_value_description(config.LOCALE_EN),
                description_italian=year_period.get_value_description(config.LOCALE_IT),
                sort_order=year_period.get_sort_order(),
                configuration_parameter_id=_FAKE_ID,
            )
        )
    return conf_param


def _get_uncertainty_type_conf_param() -> coverages.ConfigurationParameter:
    conf_param = coverages.ConfigurationParameter(
        id=_FAKE_ID,
        name="uncertainty_type",
        display_name_english="Uncertainty type",
        display_name_italian="Tipologia dei limiti di incertezza",
        description_english="Type of uncertainty that this configuration represents",
        description_italian="Tipo di incertezza che questa configurazione rappresenta",
        allowed_values=[],
    )
    for dataset_type in static.DatasetType.__members__.values():
        if "uncertainty" in dataset_type.name.lower():
            converted = legacy_schemas.convert_to_uncertainty_type(dataset_type)
            conf_param.allowed_values.append(
                coverages.ConfigurationParameterValue(
                    id=_FAKE_ID,
                    name=converted,
                    internal_value=converted,
                    display_name_english=dataset_type.get_value_display_name(
                        config.LOCALE_EN
                    ),
                    display_name_italian=dataset_type.get_value_display_name(
                        config.LOCALE_EN
                    ),
                    description_english=dataset_type.get_value_description(
                        config.LOCALE_EN
                    ),
                    description_italian=dataset_type.get_value_description(
                        config.LOCALE_IT
                    ),
                    sort_order=dataset_type.get_sort_order(),
                    configuration_parameter_id=_FAKE_ID,
                )
            )
    return conf_param


def _get_archive_conf_param() -> coverages.ConfigurationParameter:
    return coverages.ConfigurationParameter(
        id=_FAKE_ID,
        name="archive",
        display_name_english="Dataset archive",
        display_name_italian="archivio di dataset",
        description_english="The archive that the dataset belongs to",
        description_italian="L'archivio a cui appartiene il set di dati",
        allowed_values=[
            coverages.ConfigurationParameterValue(
                id=_FAKE_ID,
                name="historical",
                internal_value="historical",
                display_name_english="Historical data",
                display_name_italian="Dati storici",
                description_english=("Datasets obtained from historical data"),
                description_italian=("Set di dati ottenuti da dati storici"),
                sort_order=0,
                configuration_parameter_id=_FAKE_ID,
            ),
            coverages.ConfigurationParameterValue(
                id=_FAKE_ID,
                name="forecast",
                internal_value="forecast",
                display_name_english="Forecast data",
                display_name_italian="Dati di previsione",
                description_english=("Datasets obtained from forecasts"),
                description_italian=("Set di dati ottenuti dalle previsioni"),
                sort_order=0,
                configuration_parameter_id=_FAKE_ID,
            ),
            coverages.ConfigurationParameterValue(
                id=_FAKE_ID,
                name="barometro_climatico",
                internal_value="barometro_climatico",
                display_name_english="Climate barometer",
                display_name_italian="Barometro climatico",
                description_english="Regional overview",
                description_italian="Panoramica regionale",
                sort_order=0,
                configuration_parameter_id=_FAKE_ID,
            ),
        ],
    )


def legacy_list_configuration_parameters(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    name_filter: str | None = None,
) -> tuple[Sequence[coverages.ConfigurationParameter], Optional[int]]:
    """List existing configuration parameters."""
    # - [x] climatological variable
    # - [x] climatological model
    # - [x] measure
    # - [x] aggregation period
    # - [x] scenario
    # - [x] year period
    # - [x] time window
    # - [x] uncertainty type
    # - [x] archive
    # - [ ] historical variable
    # - [ ] historical year period
    # - [ ] climatological standard normal

    all_climatic_indicators = collect_all_climatic_indicators(session)
    configuration_parameters = [
        _get_climatological_variable_conf_param(all_climatic_indicators),
        _get_climatological_model_conf_param(session),
        _get_measure_conf_param(all_climatic_indicators),
        _get_aggregation_period_conf_param(all_climatic_indicators),
        _get_scenario_conf_param(),
        _get_year_period_conf_param(),
        _get_time_window_conf_param(session),
        _get_uncertainty_type_conf_param(),
        _get_archive_conf_param(),
    ]
    if name_filter is not None:
        filtered = [cp for cp in configuration_parameters if name_filter in cp.name]
    else:
        filtered = configuration_parameters
    result = filtered[offset : offset + limit]
    return result, len(filtered) if include_total else None


def collect_all_configuration_parameters(
    session: sqlmodel.Session,
) -> Sequence[coverages.ConfigurationParameter]:
    _, num_total = legacy_list_configuration_parameters(
        session, limit=1, include_total=True
    )
    result, _ = legacy_list_configuration_parameters(
        session, limit=num_total, include_total=False
    )
    return result


def create_configuration_parameter_value(
    session: sqlmodel.Session,
    parameter_value: coverages.ConfigurationParameterValueCreate,
) -> coverages.ConfigurationParameterValue:
    param_name = parameter_value.name or slugify_internal_value(
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
            name=allowed.name or slugify_internal_value(allowed.internal_value),
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
                name=av.name or slugify_internal_value(av.internal_value),
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
        statement = add_substring_filter(
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
    num_items = get_total_num_records(session, statement) if include_total else None
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
