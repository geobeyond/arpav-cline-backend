import logging
import uuid
from typing import (
    Final,
    Optional,
    Sequence,
)

import sqlmodel

from .. import config
from ..config import (
    LOCALE_EN,
    LOCALE_IT,
)
from ..schemas import (
    coverages,
    climaticindicators,
    legacy as legacy_schemas,
    static,
)
from ..schemas.static import (
    DataCategory,
    HistoricalReferencePeriod,
    HistoricalDecade,
    HistoricalYearPeriod,
)
from .climaticindicators import collect_all_climatic_indicators
from .forecastcoverages import (
    collect_all_forecast_models,
    collect_all_forecast_time_windows,
)

logger = logging.getLogger(__name__)

_FAKE_ID: Final[uuid.UUID] = uuid.UUID("06213c04-6872-4677-a149-a3b84f8da224")


def _get_historical_variable_conf_param(
    all_climatic_indicators: Sequence[climaticindicators.ClimaticIndicator],
):
    conf_param = coverages.ConfigurationParameter(
        id=_FAKE_ID,
        name="historical_variable",
        display_name_english="Variable",
        display_name_italian="Variabile",
        description_english="Historical variable",
        description_italian="Variabile historica",
        allowed_values=[],
    )
    seen = set()
    for indicator in all_climatic_indicators:
        for historical_cov_conf in indicator.historical_coverage_configurations:
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


def _get_historical_decade_conf_param() -> coverages.ConfigurationParameter:
    return coverages.ConfigurationParameter(
        id=_FAKE_ID,
        name="historical_decade",
        display_name_english=HistoricalDecade.get_param_display_name(LOCALE_EN),
        display_name_italian=HistoricalDecade.get_param_display_name(LOCALE_IT),
        description_english=HistoricalDecade.get_param_description(LOCALE_EN),
        description_italian=HistoricalDecade.get_param_description(LOCALE_IT),
        allowed_values=[
            coverages.ConfigurationParameterValue(
                id=_FAKE_ID,
                name=member.value,
                internal_value=member.get_internal_value(),
                display_name_english=member.get_value_display_name(LOCALE_EN),
                display_name_italian=member.get_value_display_name(LOCALE_IT),
                description_english=member.get_value_description(LOCALE_EN),
                description_italian=member.get_value_description(LOCALE_IT),
                sort_order=member.get_sort_order(),
                configuration_parameter_id=_FAKE_ID,
            )
            for member in HistoricalDecade.__members__.values()
        ],
    )


def _get_historical_year_period_conf_param() -> coverages.ConfigurationParameter:
    return coverages.ConfigurationParameter(
        id=_FAKE_ID,
        name="historical_year_period",
        display_name_english=HistoricalYearPeriod.get_param_display_name(LOCALE_EN),
        display_name_italian=HistoricalYearPeriod.get_param_display_name(LOCALE_IT),
        description_english=HistoricalYearPeriod.get_param_description(LOCALE_EN),
        description_italian=HistoricalYearPeriod.get_param_description(LOCALE_IT),
        allowed_values=[
            coverages.ConfigurationParameterValue(
                id=_FAKE_ID,
                name=member.value,
                internal_value=member.get_internal_value(),
                display_name_english=member.get_value_display_name(LOCALE_EN),
                display_name_italian=member.get_value_display_name(LOCALE_IT),
                description_english=member.get_value_description(LOCALE_EN),
                description_italian=member.get_value_description(LOCALE_IT),
                sort_order=member.get_sort_order(),
                configuration_parameter_id=_FAKE_ID,
            )
            for member in HistoricalYearPeriod.__members__.values()
        ],
    )


def _get_historical_reference_period_conf_param() -> coverages.ConfigurationParameter:
    return coverages.ConfigurationParameter(
        id=_FAKE_ID,
        name="reference_period",
        display_name_english=HistoricalReferencePeriod.get_param_display_name(
            LOCALE_EN
        ),
        display_name_italian=HistoricalReferencePeriod.get_param_display_name(
            LOCALE_IT
        ),
        description_english=HistoricalReferencePeriod.get_param_description(LOCALE_EN),
        description_italian=HistoricalReferencePeriod.get_param_description(LOCALE_IT),
        allowed_values=[
            coverages.ConfigurationParameterValue(
                id=_FAKE_ID,
                name=member.value,
                internal_value=member.get_internal_value(),
                display_name_english=member.get_value_display_name(LOCALE_EN),
                display_name_italian=member.get_value_display_name(LOCALE_IT),
                description_english=member.get_value_description(LOCALE_EN),
                description_italian=member.get_value_description(LOCALE_IT),
                sort_order=member.get_sort_order(),
                configuration_parameter_id=_FAKE_ID,
            )
            for member in HistoricalReferencePeriod.__members__.values()
        ],
    )


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
                name=DataCategory.HISTORICAL.value,
                internal_value=DataCategory.HISTORICAL.value,
                display_name_english=DataCategory.HISTORICAL.get_param_display_name(
                    LOCALE_EN
                ),
                display_name_italian=DataCategory.HISTORICAL.get_param_display_name(
                    LOCALE_IT
                ),
                description_english=DataCategory.HISTORICAL.get_param_description(
                    LOCALE_EN
                ),
                description_italian=DataCategory.HISTORICAL.get_param_description(
                    LOCALE_IT
                ),
                sort_order=DataCategory.HISTORICAL.get_sort_order(),
                configuration_parameter_id=_FAKE_ID,
            ),
            coverages.ConfigurationParameterValue(
                id=_FAKE_ID,
                name=DataCategory.FORECAST.value,
                internal_value=DataCategory.FORECAST.value,
                display_name_english=DataCategory.FORECAST.get_param_display_name(
                    LOCALE_EN
                ),
                display_name_italian=DataCategory.FORECAST.get_param_display_name(
                    LOCALE_IT
                ),
                description_english=DataCategory.FORECAST.get_param_description(
                    LOCALE_EN
                ),
                description_italian=DataCategory.FORECAST.get_param_description(
                    LOCALE_IT
                ),
                sort_order=DataCategory.FORECAST.get_sort_order(),
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
    """List existing configuration parameters"""
    # - [x] archive
    # - [x] aggregation period
    # - [x] climatological model
    # - [x] climatological variable
    # - [x] historical reference period
    # - [x] historical variable
    # - [x] historical year period
    # - [x] historical decade
    # - [x] measure
    # - [x] scenario
    # - [x] time window
    # - [x] uncertainty type
    # - [x] year period

    all_climatic_indicators = collect_all_climatic_indicators(session)
    configuration_parameters = [
        _get_aggregation_period_conf_param(all_climatic_indicators),
        _get_archive_conf_param(),
        _get_climatological_model_conf_param(session),
        _get_climatological_variable_conf_param(all_climatic_indicators),
        _get_historical_decade_conf_param(),
        _get_historical_reference_period_conf_param(),
        _get_historical_variable_conf_param(all_climatic_indicators),
        _get_historical_year_period_conf_param(),
        _get_measure_conf_param(all_climatic_indicators),
        _get_scenario_conf_param(),
        _get_year_period_conf_param(),
        _get_time_window_conf_param(session),
        _get_uncertainty_type_conf_param(),
    ]
    if name_filter is not None:
        filtered = [cp for cp in configuration_parameters if name_filter in cp.name]
    else:
        filtered = configuration_parameters
    result = filtered[offset : offset + limit]
    return result, len(filtered) if include_total else None
