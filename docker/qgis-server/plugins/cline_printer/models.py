import dataclasses


@dataclasses.dataclass(frozen=True)
class RawApiDetails:
    coverage: dict
    configuration_parameters: list[dict]
    climatic_indicator: dict


@dataclasses.dataclass(frozen=True)
class _ForecastCoverageDisplayDetails:
    title: str
    data_category: str
    description: str
    climatic_indicator: str
    measure: str
    aggregation_period: str
    model: str
    scenario: str
    year_period: str
    time_window: str | None
    full_coverage_details: dict
    unit: str


@dataclasses.dataclass(frozen=True)
class _HistoricalCoverageDisplayDetails:
    title: str
    data_category: str
    description: str
    climatic_indicator: str
    measure: str
    aggregation_period: str
    year_period: str
    full_coverage_details: dict
    decade: str | None
    reference_period: str | None
    unit: str


def _get_translated_detail(
    configuration_parameters_details: list[dict],
    name: str,
    value: str,
    lang_key: str,
    default_to: str = "",
) -> str:
    all_conf_params_details = [
        cp for cp in configuration_parameters_details if cp["name"] == name
    ][0]
    try:
        allowed_value_details = [
            av
            for av in all_conf_params_details["allowed_values"]
            if av["name"] == value
        ][0]
    except IndexError:
        result = default_to
    else:
        result = allowed_value_details[f"display_name_{lang_key}"]
    return result


def _get_forecast_display_details(
    *,
    language_code: str,
    coverage_details: dict,
    climatic_indicator_details: dict,
    configuration_parameters_details: list[dict],
) -> _ForecastCoverageDisplayDetails:
    lang_key = "italian" if language_code == "it" else "english"
    climatic_indicator_display_name = _get_translated_detail(
        configuration_parameters_details,
        "climatological_variable",
        climatic_indicator_details["name"],
        lang_key,
    )
    measure_display_name = _get_translated_detail(
        configuration_parameters_details,
        "measure",
        climatic_indicator_details["measure_type"],
        lang_key,
    )
    aggregation_period_display_name = _get_translated_detail(
        configuration_parameters_details,
        "aggregation_period",
        climatic_indicator_details["aggregation_period"],
        lang_key,
    )
    model_display_name = _get_translated_detail(
        configuration_parameters_details,
        "climatological_model",
        coverage_details["forecast_model"],
        lang_key,
    )
    scenario_display_name = _get_translated_detail(
        configuration_parameters_details,
        "scenario",
        coverage_details["scenario"],
        lang_key,
    )
    year_period_display_name = _get_translated_detail(
        configuration_parameters_details,
        "year_period",
        coverage_details["year_period"],
        lang_key,
    )
    data_category_display_name = _get_translated_detail(
        configuration_parameters_details, "archive", "forecast", lang_key
    )
    unit_display_name = coverage_details[f"unit_{lang_key}"]
    try:
        time_window_display_name = _get_translated_detail(
            configuration_parameters_details,
            "time_window",
            coverage_details["time_window"],
            lang_key,
        )
    except IndexError:
        time_window_display_name = None
    return _ForecastCoverageDisplayDetails(
        title=coverage_details[f"display_name_{lang_key}"],
        data_category=data_category_display_name,
        description=coverage_details[f"description_{lang_key}"],
        climatic_indicator=climatic_indicator_display_name,
        measure=measure_display_name,
        aggregation_period=aggregation_period_display_name,
        model=model_display_name,
        scenario=scenario_display_name,
        year_period=year_period_display_name,
        time_window=time_window_display_name,
        unit=unit_display_name,
        full_coverage_details=coverage_details,
    )


def _get_historical_display_details(
    *,
    language_code: str,
    coverage_details: dict,
    climatic_indicator_details: dict,
    configuration_parameters_details: list[dict],
) -> _HistoricalCoverageDisplayDetails:
    lang_key = "italian" if language_code == "it" else "english"
    climatic_indicator_display_name = _get_translated_detail(
        configuration_parameters_details,
        "climatological_variable",
        climatic_indicator_details["name"],
        lang_key,
    )
    measure_display_name = _get_translated_detail(
        configuration_parameters_details,
        "measure",
        climatic_indicator_details["measure_type"],
        lang_key,
    )
    aggregation_period_display_name = _get_translated_detail(
        configuration_parameters_details,
        "aggregation_period",
        climatic_indicator_details["aggregation_period"],
        lang_key,
    )
    year_period_display_name = _get_translated_detail(
        configuration_parameters_details,
        "historical_year_period",
        coverage_details["year_period"],
        lang_key,
    )
    decade_display_name = _get_translated_detail(
        configuration_parameters_details,
        "historical_decade",
        coverage_details["decade"],
        lang_key,
    )
    reference_period_display_name = _get_translated_detail(
        configuration_parameters_details,
        "reference_period",
        coverage_details["reference_period"],
        lang_key,
    )
    data_category_display_name = _get_translated_detail(
        configuration_parameters_details, "archive", "historical", lang_key
    )
    unit_display_name = coverage_details[f"unit_{lang_key}"]
    return _HistoricalCoverageDisplayDetails(
        title=coverage_details[f"display_name_{lang_key}"],
        data_category=data_category_display_name,
        description=coverage_details[f"description_{lang_key}"],
        climatic_indicator=climatic_indicator_display_name,
        measure=measure_display_name,
        aggregation_period=aggregation_period_display_name,
        year_period=year_period_display_name,
        decade=decade_display_name,
        reference_period=reference_period_display_name,
        unit=unit_display_name,
        full_coverage_details=coverage_details,
    )


@dataclasses.dataclass(frozen=True)
class ForecastMapLayoutVariables:
    title: str
    data_category: str
    description: str
    climatic_indicator: str
    quantity_and_period: str
    model: str
    scenario: str
    year_period: str
    parameter_climatic_indicator: str
    parameter_model_and_scenario: str
    parameter_quantity_and_period: str
    parameter_season: str
    section_map_details_title: str
    legend_title: str

    @classmethod
    def from_api_details(
        cls, api_details: RawApiDetails, language_code: str
    ) -> "ForecastMapLayoutVariables":
        display_details = _get_forecast_display_details(
            language_code=language_code,
            coverage_details=api_details.coverage,
            climatic_indicator_details=api_details.climatic_indicator,
            configuration_parameters_details=api_details.configuration_parameters,
        )
        quantity_and_period = (
            f"{display_details.aggregation_period} - {display_details.measure}"
        )
        if display_details.time_window != "":
            quantity_and_period = " - ".join(
                (quantity_and_period, display_details.time_window)
            )
        return ForecastMapLayoutVariables(
            title=display_details.title,
            data_category=display_details.data_category,
            description=display_details.description,
            climatic_indicator=display_details.climatic_indicator,
            quantity_and_period=quantity_and_period,
            model=display_details.model,
            scenario=display_details.scenario,
            year_period=display_details.year_period,
            parameter_climatic_indicator=(
                "Indicatore" if language_code == "it" else "Indicator"
            ),
            parameter_model_and_scenario=(
                "Modello e Scenario" if language_code == "it" else "Model and Scenario"
            ),
            parameter_quantity_and_period=(
                "Quantità e Periodo" if language_code == "it" else "Quantity and Period"
            ),
            parameter_season=("Stagione" if language_code == "it" else "Season"),
            section_map_details_title=(
                "Informazioni sulla mappa" if language_code == "it" else "Map Info"
            ),
            legend_title=f"{display_details.title} ({display_details.unit})",
        )


@dataclasses.dataclass(frozen=True)
class HistoricalMapLayoutVariables:
    title: str
    data_category: str
    description: str
    climatic_indicator: str
    quantity_and_period: str
    parameter_climatic_indicator: str
    parameter_quantity_and_period: str
    parameter_season: str
    section_map_details_title: str
    legend_title: str
    year_period: str

    @classmethod
    def from_api_details(
        cls, api_details: RawApiDetails, language_code: str
    ) -> "HistoricalMapLayoutVariables":
        display_details = _get_historical_display_details(
            language_code=language_code,
            coverage_details=api_details.coverage,
            climatic_indicator_details=api_details.climatic_indicator,
            configuration_parameters_details=api_details.configuration_parameters,
        )
        quantity_and_period = (
            f"{display_details.aggregation_period} - {display_details.measure}"
        )
        if display_details.reference_period != "":
            quantity_and_period = " - ".join(
                (quantity_and_period, display_details.reference_period)
            )
        if display_details.decade != "":
            quantity_and_period = " - ".join(
                (quantity_and_period, display_details.decade)
            )
        return HistoricalMapLayoutVariables(
            title=display_details.title,
            data_category=display_details.data_category,
            description=display_details.description,
            climatic_indicator=display_details.climatic_indicator,
            quantity_and_period=quantity_and_period,
            year_period=display_details.year_period,
            parameter_climatic_indicator=(
                "Indicatore" if language_code == "it" else "Indicator"
            ),
            parameter_quantity_and_period=(
                "Quantità e Periodo" if language_code == "it" else "Quantity and Period"
            ),
            parameter_season=("Stagione" if language_code == "it" else "Season"),
            section_map_details_title=(
                "Informazioni sulla mappa" if language_code == "it" else "Map Info"
            ),
            legend_title=f"{display_details.title} ({display_details.unit})",
        )
