import dataclasses
import pydantic
import typing

from ...config import (
    LOCALE_EN,
    LOCALE_IT,
)
from ...schemas.base import StaticCoverageSeriesParameter

if typing.TYPE_CHECKING:
    from ...schemas.climaticindicators import ClimaticIndicator
    from ...schemas import dataseries
    from ...schemas import coverages
    from ...schemas import static


@dataclasses.dataclass
class ForecastCoverageNavigationSection:
    climatic_indicator: "ClimaticIndicator"
    forecast_models: list["coverages.ForecastModel"] = dataclasses.field(default_factory=list)
    scenarios: list["static.ForecastScenario"] = dataclasses.field(default_factory=list)
    year_periods: list["static.ForecastYearPeriod"] = dataclasses.field(default_factory=list)
    time_windows: list["coverages.ForecastTimeWindow"] = dataclasses.field(default_factory=list)


class LegacyForecastVariableCombinations(pydantic.BaseModel):
    variable: str
    aggregation_period: str
    measure: str
    other_parameters: dict[str, list[str]]

    @classmethod
    def from_navigation_section(
        cls, section: ForecastCoverageNavigationSection
    ):
        other = {
            "climatological_model": [fm.name for fm in section.forecast_models],
            "scenario": [s.value for s in section.scenarios],
            "year_period": [yp.value for yp in section.year_periods],
        }
        if len(section.time_windows) > 0:
            other["time_window"] = [tw.name for tw in section.time_windows]
        return cls(
            variable=section.climatic_indicator.name,
            aggregation_period=section.climatic_indicator.aggregation_period.value,
            measure=section.climatic_indicator.measure_type.value,
            other_parameters=other
        )


class LegacyTimeSeriesTranslations(pydantic.BaseModel):
    parameter_names: typing.Optional[dict[str, dict[str, str]]] = None
    parameter_values: typing.Optional[dict[str, dict[str, str]]] = None

    @classmethod
    def from_forecast_data_series(cls, series: "dataseries.ForecastDataSeries"):
        return cls(
            # FIXME: get rid of all the StaticCoverageSeriesParameter stuff
            parameter_names={
                "series_name": {
                    LOCALE_EN.language: StaticCoverageSeriesParameter.SERIES_NAME.get_display_name(LOCALE_EN),
                    LOCALE_IT.language: StaticCoverageSeriesParameter.SERIES_NAME.get_display_name(LOCALE_IT),
                },
                "processing_method": {
                    LOCALE_EN.language: series.smoothing_strategy.get_param_display_name(LOCALE_EN),
                    LOCALE_IT.language: series.smoothing_strategy.get_param_display_name(LOCALE_IT),
                },
                "coverage_identifier": {
                    LOCALE_EN.language: StaticCoverageSeriesParameter.COVERAGE_IDENTIFIER.get_display_name(LOCALE_EN),
                    LOCALE_IT.language: StaticCoverageSeriesParameter.COVERAGE_IDENTIFIER.get_display_name(LOCALE_IT),
                },
                "coverage_configuration": {
                    LOCALE_EN.language: StaticCoverageSeriesParameter.COVERAGE_CONFIGURATION.get_display_name(LOCALE_EN),
                    LOCALE_IT.language: StaticCoverageSeriesParameter.COVERAGE_CONFIGURATION.get_display_name(LOCALE_IT),
                },
                "aggregation_period": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.configuration.climatic_indicator
                        .aggregation_period.get_param_display_name(LOCALE_EN)
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.configuration.climatic_indicator
                        .aggregation_period.get_param_display_name(LOCALE_IT)
                    ),
                },
                "climatological_model": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.forecast_model.get_display_name(
                            LOCALE_EN)
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.forecast_model.get_display_name(
                            LOCALE_IT)
                    ),
                },
                "climatological_variable": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.configuration
                        .climatic_indicator.get_display_name(LOCALE_EN)
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.configuration
                        .climatic_indicator.get_display_name(LOCALE_IT)
                    ),
                },
                "measure": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.configuration
                        .climatic_indicator.measure_type.get_param_display_name(
                            LOCALE_EN
                        )
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.configuration
                        .climatic_indicator.measure_type.get_param_display_name(
                            LOCALE_IT
                        )
                    ),
                },
                "scenario": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.scenario.get_param_display_name(
                            LOCALE_EN)
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.scenario.get_param_display_name(
                            LOCALE_IT)
                    ),
                },
                "year_period": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.forecast_year_period
                        .get_param_display_name(LOCALE_EN)
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.forecast_year_period
                        .get_param_display_name(LOCALE_IT)
                    ),
                },
            },
            parameter_values={
                "series_name": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.configuration.climatic_indicator
                        .description_english
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.configuration.climatic_indicator
                        .description_italian
                    ),
                },
                "processing_method": {
                    LOCALE_EN.language: (
                        series.smoothing_strategy.get_value_display_name(LOCALE_EN),
                    ),
                    LOCALE_IT.language: (
                        series.smoothing_strategy.get_value_display_name(LOCALE_IT),
                    ),
                },
                "coverage_identifier": {
                    LOCALE_EN.language: series.forecast_coverage.identifier,
                    LOCALE_IT.language: series.forecast_coverage.identifier,
                },
                "coverage_configuration": {
                    LOCALE_EN.language: series.forecast_coverage.configuration.identifier,
                    LOCALE_IT.language: series.forecast_coverage.configuration.identifier,
                },
                "aggregation_period": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.configuration.climatic_indicator
                        .aggregation_period.get_value_display_name(LOCALE_EN)
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.configuration.climatic_indicator
                        .aggregation_period.get_value_display_name(LOCALE_IT)
                    ),
                },
                "climatological_model": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.forecast_model.display_name_english
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.forecast_model.display_name_italian
                    ),
                },
                "climatological_variable": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.configuration.climatic_indicator
                        .display_name_english,
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.configuration.climatic_indicator
                        .display_name_italian,
                    ),
                },
                "measure": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.configuration.climatic_indicator
                        .measure_type.get_value_display_name(LOCALE_EN),
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.configuration.climatic_indicator
                        .measure_type.get_value_display_name(LOCALE_IT),
                    ),
                },
                "scenario": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.scenario.get_value_display_name(
                            LOCALE_EN),
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.scenario.get_value_display_name(
                            LOCALE_IT),
                    ),
                },
                "year_period": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.forecast_year_period
                        .get_value_display_name(LOCALE_EN),
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.forecast_year_period
                        .get_value_display_name(LOCALE_IT),
                    ),
                },
            },
        )


class LegacyConfigurationParameterMenuTranslation(pydantic.BaseModel):
    name: dict[str, str]
    description: dict[str, str]


class LegacyForecastMenuTranslations(pydantic.BaseModel):
    variable: dict[str, LegacyConfigurationParameterMenuTranslation]
    aggregation_period: dict[str, LegacyConfigurationParameterMenuTranslation]
    measure: dict[str, LegacyConfigurationParameterMenuTranslation]
    other_parameters: dict[str, dict[str, LegacyConfigurationParameterMenuTranslation]]

    @classmethod
    def from_navigation_sections(
        cls,
        sections: list[ForecastCoverageNavigationSection]
    ):
        vars = {}
        aggreg_periods = {}
        measures = {}
        other = {
            "year_period": {},
            "scenario": {},
            "climatological_model": {},
            "time_window": {},
        }
        unique_year_periods = set()
        unique_scenarios = set()
        unique_models = set()
        unique_time_windows = set()
        for section in sections:
            vars[section.climatic_indicator.name] = LegacyConfigurationParameterMenuTranslation(
                name={
                    LOCALE_EN.language: section.climatic_indicator.display_name_english,
                    LOCALE_IT.language: section.climatic_indicator.display_name_italian,
                },
                description={
                    LOCALE_EN.language: section.climatic_indicator.description_english,
                    LOCALE_IT.language: section.climatic_indicator.description_italian,
                },
            )
            unique_year_periods.update(section.year_periods)
            unique_scenarios.update(section.scenarios)
            unique_models.update(section.forecast_models)
            unique_time_windows.update(section.time_windows)
        unique_aggregation_periods = {
            s.climatic_indicator.aggregation_period for s in sections}
        for aggregation_period in unique_aggregation_periods:
            aggreg_periods[aggregation_period.value] = LegacyConfigurationParameterMenuTranslation(
                name={
                    LOCALE_EN.language: aggregation_period.get_value_display_name(
                        LOCALE_EN),
                    LOCALE_IT.language: aggregation_period.get_value_display_name(
                        LOCALE_IT),
                },
                description={
                    LOCALE_EN.language: aggregation_period.get_value_description(
                        LOCALE_EN),
                    LOCALE_IT.language: aggregation_period.get_value_description(
                        LOCALE_IT),
                }
            )
        for measure_type in {s.climatic_indicator.measure_type for s in sections}:
            measures[measure_type.value] = LegacyConfigurationParameterMenuTranslation(
                name={
                    LOCALE_EN.language: measure_type.get_value_display_name(
                        LOCALE_EN),
                    LOCALE_IT.language: measure_type.get_value_display_name(
                        LOCALE_IT),
                },
                description={
                    LOCALE_EN.language: measure_type.get_value_description(
                        LOCALE_EN),
                    LOCALE_IT.language: measure_type.get_value_description(
                        LOCALE_IT),
                }
            )
        for year_period in unique_year_periods:
            other["year_period"][year_period.value] = LegacyConfigurationParameterMenuTranslation(
                name={
                    LOCALE_EN.language: year_period.get_value_display_name(
                        LOCALE_EN),
                    LOCALE_IT.language: year_period.get_value_display_name(
                        LOCALE_IT),
                },
                description={
                    LOCALE_EN.language: year_period.get_value_description(
                        LOCALE_EN),
                    LOCALE_IT.language: year_period.get_value_description(
                        LOCALE_IT),
                },
            )
        for scenario in unique_scenarios:
            other["scenario"][scenario.value] = LegacyConfigurationParameterMenuTranslation(
                name={
                    LOCALE_EN.language: scenario.get_value_display_name(
                        LOCALE_EN),
                    LOCALE_IT.language: scenario.get_value_display_name(
                        LOCALE_IT),
                },
                description={
                    LOCALE_EN.language: scenario.get_value_description(
                        LOCALE_EN),
                    LOCALE_IT.language: scenario.get_value_description(
                        LOCALE_IT),
                },
            )
        for forecast_model in unique_models:
            other["climatological_model"][forecast_model.name] = LegacyConfigurationParameterMenuTranslation(
                name={
                    LOCALE_EN.language: forecast_model.display_name_english,
                    LOCALE_IT.language: forecast_model.display_name_italian,
                },
                description={
                    LOCALE_EN.language: forecast_model.description_english,
                    LOCALE_IT.language: forecast_model.description_italian,
                },
            )
        for time_window in unique_time_windows:
            other["time_window"][time_window.name] = LegacyConfigurationParameterMenuTranslation(
                name={
                    LOCALE_EN.language: time_window.display_name_english,
                    LOCALE_IT.language: time_window.display_name_italian,
                },
                description={
                    LOCALE_EN.language: time_window.description_english,
                    LOCALE_IT.language: time_window.description_italian,
                },
            )
        return cls(
            variable=vars,
            aggregation_period=aggreg_periods,
            measure=measures,
            other_parameters=other
        )


class LegacyForecastVariableCombinationsList(pydantic.BaseModel):
    combinations: list[LegacyForecastVariableCombinations]
    translations: LegacyForecastMenuTranslations
