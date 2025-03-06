import dataclasses
import pydantic
import typing

from ...config import (
    LOCALE_EN,
    LOCALE_IT,
)
from ...schemas import static
from ...schemas import legacy as legacy_schemas

if typing.TYPE_CHECKING:
    from ...schemas.climaticindicators import ClimaticIndicator
    from ...schemas import coverages


@dataclasses.dataclass
class ForecastCoverageNavigationSection:
    climatic_indicator: "ClimaticIndicator"
    forecast_models: list["coverages.ForecastModel"] = dataclasses.field(
        default_factory=list
    )
    scenarios: list[static.ForecastScenario] = dataclasses.field(default_factory=list)
    year_periods: list[static.ForecastYearPeriod] = dataclasses.field(
        default_factory=list
    )
    time_windows: list["coverages.ForecastTimeWindow"] = dataclasses.field(
        default_factory=list
    )


@dataclasses.dataclass
class HistoricalCoverageNavigationSection:
    climatic_indicator: "ClimaticIndicator"
    year_periods: list[static.HistoricalYearPeriod] = dataclasses.field(
        default_factory=list
    )
    reference_periods: list[static.HistoricalReferencePeriod] = dataclasses.field(
        default_factory=list
    )
    decades: list[static.HistoricalDecade] = dataclasses.field(default_factory=list)


class LegacyForecastVariableCombinations(pydantic.BaseModel):
    climatological_variable: str
    aggregation_period: str
    measure: str
    other_parameters: dict[str, list[str]]

    @classmethod
    def from_navigation_section(cls, section: ForecastCoverageNavigationSection):
        other = {
            "archive": [
                static.DataCategory.FORECAST.value,
            ],
            "climatological_model": [fm.name for fm in section.forecast_models],
            "scenario": [s.value for s in section.scenarios],
            "year_period": [yp.value for yp in section.year_periods],
        }
        if len(section.time_windows) > 0:
            other["time_window"] = [tw.name for tw in section.time_windows]
        return cls(
            climatological_variable=section.climatic_indicator.name,
            aggregation_period=legacy_schemas.convert_to_aggregation_period(
                section.climatic_indicator.aggregation_period
            ),
            measure=section.climatic_indicator.measure_type.value,
            other_parameters=other,
        )


class LegacyHistoricalVariableCombinations(pydantic.BaseModel):
    climatological_variable: str
    aggregation_period: str
    measure: str
    other_parameters: dict[str, list[str]]

    @classmethod
    def from_navigation_section(cls, section: HistoricalCoverageNavigationSection):
        other = {
            "archive": [
                static.DataCategory.HISTORICAL.value,
            ],
            "year_period": [yp.value for yp in section.year_periods],
        }
        if len(section.reference_periods) > 0:
            other["reference_period"] = [rp.value for rp in section.reference_periods]
        if len(section.decades) > 0:
            other["decade"] = [d.value for d in section.decades]
        return cls(
            climatological_variable=section.climatic_indicator.name,
            aggregation_period=legacy_schemas.convert_to_aggregation_period(
                section.climatic_indicator.aggregation_period
            ),
            measure=section.climatic_indicator.measure_type.value,
            other_parameters=other,
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
        cls, sections: list[ForecastCoverageNavigationSection]
    ):
        vars = {}
        aggreg_periods = {}
        measures = {}
        other = {
            "year_period": {},
            "archive": {
                static.DataCategory.FORECAST.value: LegacyConfigurationParameterMenuTranslation(
                    name={
                        LOCALE_EN.language: "Forecast data",
                        LOCALE_IT.language: "Forecast data",
                    },
                    description={
                        LOCALE_EN.language: "Forecast data",
                        LOCALE_IT.language: "Forecast data",
                    },
                ),
            },
            "scenario": {},
            "climatological_model": {},
            "time_window": {},
        }
        unique_year_periods = set()
        unique_scenarios = set()
        unique_models = set()
        unique_time_windows = set()
        for section in sections:
            vars[
                section.climatic_indicator.name
            ] = LegacyConfigurationParameterMenuTranslation(
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
            s.climatic_indicator.aggregation_period for s in sections
        }
        for aggregation_period in unique_aggregation_periods:
            aggreg_periods[
                legacy_schemas.convert_to_aggregation_period(aggregation_period)
            ] = LegacyConfigurationParameterMenuTranslation(
                name={
                    LOCALE_EN.language: aggregation_period.get_value_display_name(
                        LOCALE_EN
                    ),
                    LOCALE_IT.language: aggregation_period.get_value_display_name(
                        LOCALE_IT
                    ),
                },
                description={
                    LOCALE_EN.language: aggregation_period.get_value_description(
                        LOCALE_EN
                    ),
                    LOCALE_IT.language: aggregation_period.get_value_description(
                        LOCALE_IT
                    ),
                },
            )
        for measure_type in {s.climatic_indicator.measure_type for s in sections}:
            measures[measure_type.value] = LegacyConfigurationParameterMenuTranslation(
                name={
                    LOCALE_EN.language: measure_type.get_value_display_name(LOCALE_EN),
                    LOCALE_IT.language: measure_type.get_value_display_name(LOCALE_IT),
                },
                description={
                    LOCALE_EN.language: measure_type.get_value_description(LOCALE_EN),
                    LOCALE_IT.language: measure_type.get_value_description(LOCALE_IT),
                },
            )
        for year_period in unique_year_periods:
            other["year_period"][
                year_period.value
            ] = LegacyConfigurationParameterMenuTranslation(
                name={
                    LOCALE_EN.language: year_period.get_value_display_name(LOCALE_EN),
                    LOCALE_IT.language: year_period.get_value_display_name(LOCALE_IT),
                },
                description={
                    LOCALE_EN.language: year_period.get_value_description(LOCALE_EN),
                    LOCALE_IT.language: year_period.get_value_description(LOCALE_IT),
                },
            )
        for scenario in unique_scenarios:
            other["scenario"][
                scenario.value
            ] = LegacyConfigurationParameterMenuTranslation(
                name={
                    LOCALE_EN.language: scenario.get_value_display_name(LOCALE_EN),
                    LOCALE_IT.language: scenario.get_value_display_name(LOCALE_IT),
                },
                description={
                    LOCALE_EN.language: scenario.get_value_description(LOCALE_EN),
                    LOCALE_IT.language: scenario.get_value_description(LOCALE_IT),
                },
            )
        for forecast_model in unique_models:
            other["climatological_model"][
                forecast_model.name
            ] = LegacyConfigurationParameterMenuTranslation(
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
            other["time_window"][
                time_window.name
            ] = LegacyConfigurationParameterMenuTranslation(
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
            other_parameters=other,
        )


class LegacyHistoricalMenuTranslations(pydantic.BaseModel):
    variable: dict[str, LegacyConfigurationParameterMenuTranslation]
    aggregation_period: dict[str, LegacyConfigurationParameterMenuTranslation]
    measure: dict[str, LegacyConfigurationParameterMenuTranslation]
    other_parameters: dict[str, dict[str, LegacyConfigurationParameterMenuTranslation]]

    @classmethod
    def from_navigation_sections(
        cls, sections: list[HistoricalCoverageNavigationSection]
    ):
        vars = {}
        aggreg_periods = {}
        measures = {}
        other = {
            "year_period": {},
            "archive": {
                static.DataCategory.HISTORICAL.value: LegacyConfigurationParameterMenuTranslation(
                    name={
                        LOCALE_EN.language: "Historical data",
                        LOCALE_IT.language: "Historical data",
                    },
                    description={
                        LOCALE_EN.language: "Historical data",
                        LOCALE_IT.language: "Historical data",
                    },
                ),
            },
            "decade": {},
            "reference_period": {},
        }
        unique_year_periods = set()
        unique_reference_periods = set()
        unique_decades = set()
        for section in sections:
            vars[
                section.climatic_indicator.name
            ] = LegacyConfigurationParameterMenuTranslation(
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
            unique_decades.update(section.decades)
            unique_reference_periods.update(section.reference_periods)
        unique_aggregation_periods = {
            s.climatic_indicator.aggregation_period for s in sections
        }
        for aggregation_period in unique_aggregation_periods:
            aggreg_periods[
                legacy_schemas.convert_to_aggregation_period(aggregation_period)
            ] = LegacyConfigurationParameterMenuTranslation(
                name={
                    LOCALE_EN.language: aggregation_period.get_value_display_name(
                        LOCALE_EN
                    ),
                    LOCALE_IT.language: aggregation_period.get_value_display_name(
                        LOCALE_IT
                    ),
                },
                description={
                    LOCALE_EN.language: aggregation_period.get_value_description(
                        LOCALE_EN
                    ),
                    LOCALE_IT.language: aggregation_period.get_value_description(
                        LOCALE_IT
                    ),
                },
            )
        for measure_type in {s.climatic_indicator.measure_type for s in sections}:
            measures[measure_type.value] = LegacyConfigurationParameterMenuTranslation(
                name={
                    LOCALE_EN.language: measure_type.get_value_display_name(LOCALE_EN),
                    LOCALE_IT.language: measure_type.get_value_display_name(LOCALE_IT),
                },
                description={
                    LOCALE_EN.language: measure_type.get_value_description(LOCALE_EN),
                    LOCALE_IT.language: measure_type.get_value_description(LOCALE_IT),
                },
            )

        for key, unique_values in (
            ("year_period", unique_year_periods),
            ("decade", unique_decades),
            ("reference_period", unique_reference_periods),
        ):
            for unique_value in unique_values:
                other[key][
                    unique_value.value
                ] = LegacyConfigurationParameterMenuTranslation(
                    name={
                        LOCALE_EN.language: unique_value.get_value_display_name(
                            LOCALE_EN
                        ),
                        LOCALE_IT.language: unique_value.get_value_display_name(
                            LOCALE_IT
                        ),
                    },
                    description={
                        LOCALE_EN.language: unique_value.get_value_description(
                            LOCALE_EN
                        ),
                        LOCALE_IT.language: unique_value.get_value_description(
                            LOCALE_IT
                        ),
                    },
                )
        return cls(
            variable=vars,
            aggregation_period=aggreg_periods,
            measure=measures,
            other_parameters=other,
        )


class LegacyForecastVariableCombinationsList(pydantic.BaseModel):
    combinations: list[LegacyForecastVariableCombinations]
    translations: LegacyForecastMenuTranslations


class LegacyHistoricalVariableCombinationsList(pydantic.BaseModel):
    combinations: list[LegacyHistoricalVariableCombinations]
    translations: LegacyHistoricalMenuTranslations
