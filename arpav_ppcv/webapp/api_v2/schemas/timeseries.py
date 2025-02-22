import datetime as dt
import logging
import math
import typing

import pydantic

from ....config import (
    LOCALE_EN,
    LOCALE_IT,
)
from ....schemas import (
    legacy,
    static,
)
from ....schemas.base import StaticCoverageSeriesParameter

if typing.TYPE_CHECKING:
    from ....schemas import dataseries

logger = logging.getLogger(__name__)


class TimeSeriesItem(pydantic.BaseModel):
    value: float
    datetime: dt.datetime


class LegacyTimeSeriesTranslations(pydantic.BaseModel):
    parameter_names: typing.Optional[dict[str, dict[str, str]]] = None
    parameter_values: typing.Optional[dict[str, dict[str, str]]] = None

    @classmethod
    def from_forecast_data_series(cls, series: "dataseries.ForecastDataSeries"):
        return cls(
            # FIXME: get rid of all the StaticCoverageSeriesParameter stuff
            parameter_names={
                "series_name": {
                    LOCALE_EN.language: StaticCoverageSeriesParameter.SERIES_NAME.get_display_name(
                        LOCALE_EN
                    ),
                    LOCALE_IT.language: StaticCoverageSeriesParameter.SERIES_NAME.get_display_name(
                        LOCALE_IT
                    ),
                },
                "processing_method": {
                    LOCALE_EN.language: series.processing_method.get_param_display_name(
                        LOCALE_EN
                    ),
                    LOCALE_IT.language: series.processing_method.get_param_display_name(
                        LOCALE_IT
                    ),
                },
                "coverage_identifier": {
                    LOCALE_EN.language: StaticCoverageSeriesParameter.COVERAGE_IDENTIFIER.get_display_name(
                        LOCALE_EN
                    ),
                    LOCALE_IT.language: StaticCoverageSeriesParameter.COVERAGE_IDENTIFIER.get_display_name(
                        LOCALE_IT
                    ),
                },
                "coverage_configuration": {
                    LOCALE_EN.language: StaticCoverageSeriesParameter.COVERAGE_CONFIGURATION.get_display_name(
                        LOCALE_EN
                    ),
                    LOCALE_IT.language: StaticCoverageSeriesParameter.COVERAGE_CONFIGURATION.get_display_name(
                        LOCALE_IT
                    ),
                },
                "aggregation_period": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.configuration.climatic_indicator.aggregation_period.get_param_display_name(
                            LOCALE_EN
                        )
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.configuration.climatic_indicator.aggregation_period.get_param_display_name(
                            LOCALE_IT
                        )
                    ),
                },
                "climatological_model": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.forecast_model.get_display_name(
                            LOCALE_EN
                        )
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.forecast_model.get_display_name(
                            LOCALE_IT
                        )
                    ),
                },
                "climatological_variable": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.configuration.climatic_indicator.get_display_name(
                            LOCALE_EN
                        )
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.configuration.climatic_indicator.get_display_name(
                            LOCALE_IT
                        )
                    ),
                },
                "measure": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.configuration.climatic_indicator.measure_type.get_param_display_name(
                            LOCALE_EN
                        )
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.configuration.climatic_indicator.measure_type.get_param_display_name(
                            LOCALE_IT
                        )
                    ),
                },
                "scenario": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.scenario.get_param_display_name(
                            LOCALE_EN
                        )
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.scenario.get_param_display_name(
                            LOCALE_IT
                        )
                    ),
                },
                "year_period": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.year_period.get_param_display_name(
                            LOCALE_EN
                        )
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.year_period.get_param_display_name(
                            LOCALE_IT
                        )
                    ),
                },
            },
            parameter_values={
                "series_name": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.configuration.climatic_indicator.description_english
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.configuration.climatic_indicator.description_italian
                    ),
                },
                "processing_method": {
                    LOCALE_EN.language: (
                        series.processing_method.get_value_display_name(LOCALE_EN)
                    ),
                    LOCALE_IT.language: (
                        series.processing_method.get_value_display_name(LOCALE_IT)
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
                        series.forecast_coverage.configuration.climatic_indicator.aggregation_period.get_value_display_name(
                            LOCALE_EN
                        )
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.configuration.climatic_indicator.aggregation_period.get_value_display_name(
                            LOCALE_IT
                        )
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
                        series.forecast_coverage.configuration.climatic_indicator.display_name_english
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.configuration.climatic_indicator.display_name_italian
                    ),
                },
                "measure": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.configuration.climatic_indicator.measure_type.get_value_display_name(
                            LOCALE_EN
                        )
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.configuration.climatic_indicator.measure_type.get_value_display_name(
                            LOCALE_IT
                        )
                    ),
                },
                "scenario": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.scenario.get_value_display_name(
                            LOCALE_EN
                        )
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.scenario.get_value_display_name(
                            LOCALE_IT
                        )
                    ),
                },
                "year_period": {
                    LOCALE_EN.language: (
                        series.forecast_coverage.year_period.get_value_display_name(
                            LOCALE_EN
                        )
                    ),
                    LOCALE_IT.language: (
                        series.forecast_coverage.year_period.get_value_display_name(
                            LOCALE_IT
                        )
                    ),
                },
            },
        )

    @classmethod
    def from_observation_station_data_series(
        cls, series: "dataseries.ObservationStationDataSeries"
    ):
        names = {}
        values = {}
        for key_name in (
            "series_name",
            "processing_method",
            "station",
            "variable",
            "series_elaboriation",
            "derived_series",
        ):
            names[key_name] = {}
            values[key_name] = {}
        for locale in (LOCALE_EN, LOCALE_IT):
            names["series_name"][locale.language] = series.get_display_name(locale)
            values["series_name"][locale.language] = series.identifier

            names["processing_method"][
                locale.language
            ] = static.ObservationTimeSeriesProcessingMethod.get_param_display_name(
                locale
            )
            values["processing_method"][
                locale.language
            ] = series.processing_method.get_value_display_name(locale)

            names["station"][
                locale.language
            ] = series.observation_station.get_display_name(locale)
            values["station"][locale.language] = series.observation_station.code

            names["variable"][
                locale.language
            ] = series.observation_series_configuration.climatic_indicator.get_display_name(
                locale
            )
            values["variable"][locale.language] = {
                LOCALE_EN: series.observation_series_configuration.climatic_indicator.display_name_english,
                LOCALE_IT: series.observation_series_configuration.climatic_indicator.display_name_italian,
            }.get(
                locale,
                series.observation_series_configuration.climatic_indicator.identifier,
            )

            names["series_elaboration"][locale.language] = names["processing_method"][
                locale.language
            ]
            values["series_elaboration"][locale.language] = values["processing_method"][
                locale.language
            ]

            names["derived_series"][locale.language] = names["processing_method"][
                locale.language
            ]
            values["derived_series"][locale.language] = values["processing_method"][
                locale.language
            ]
        return cls(parameter_names=names, parameter_values=values)

    @classmethod
    def from_forecast_overview_data_series(
        cls, series: "dataseries.ForecastOverviewDataSeries"
    ):
        names = {}
        values = {}
        for key_name in (
            "series_name",
            "series_configuration",
            "climatic_indicator",
            "processing_method",
            "coverage_identifier",
            "coverage_configuration",
            "archive",
            "climatological_variable",
            "scenario",
        ):
            names[key_name] = {}
            values[key_name] = {}
        for locale in (LOCALE_EN, LOCALE_IT):
            names["series_name"][locale.language] = series.get_display_name(locale)
            values["series_name"][locale.language] = series.identifier

            names["series_configuration"][
                locale.language
            ] = series.overview_series.configuration.get_display_name(locale)
            values["series_configuration"][
                locale.language
            ] = series.overview_series.configuration.identifier

            names["climatic_indicator"][
                locale.language
            ] = series.overview_series.configuration.climatic_indicator.get_display_name(
                locale
            )
            values["climatic_indicator"][locale.language] = {
                LOCALE_EN: series.overview_series.configuration.climatic_indicator.display_name_english,
                LOCALE_IT: series.overview_series.configuration.climatic_indicator.display_name_italian,
            }[locale]

            names["processing_method"][
                locale.language
            ] = static.CoverageTimeSeriesProcessingMethod.get_param_display_name(locale)
            values["processing_method"][
                locale.language
            ] = series.processing_method.get_value_display_name(locale)

            names["coverage_identifier"][locale.language] = series.get_display_name(
                locale
            )
            values["coverage_identifier"][locale.language] = series.identifier
            names["coverage_configuration"][
                locale.language
            ] = series.overview_series.configuration.get_display_name(locale)
            values["coverage_configuration"][
                locale.language
            ] = series.overview_series.configuration.identifier

            names["archive"][
                locale.language
            ] = static.DataCategory.get_param_display_name(locale)
            values["archive"][locale.language] = "barometro_climatico"

            names["climatological_variable"][
                locale.language
            ] = series.overview_series.configuration.climatic_indicator.get_display_name(
                locale
            )
            values["climatological_variable"][locale.language] = {
                LOCALE_EN: series.overview_series.configuration.climatic_indicator.display_name_english,
                LOCALE_IT: series.overview_series.configuration.climatic_indicator.display_name_italian,
            }.get(
                locale,
                series.overview_series.configuration.climatic_indicator.identifier,
            )

            names["scenario"][
                locale.language
            ] = static.ForecastScenario.get_param_display_name(locale)
            values["scenario"][
                locale.language
            ] = series.overview_series.scenario.get_value_display_name(locale)

        return cls(parameter_names=names, parameter_values=values)

    @classmethod
    def from_historical_overview_data_series(
        cls, series: "dataseries.ObservationOverviewDataSeries"
    ):
        names = {}
        values = {}
        for key_name in (
            "series_name",
            "processing_method",
            "series_configuration",
            "climatological_variable",
            "measure",
            "aggregation_period",
        ):
            names[key_name] = {}
            values[key_name] = {}
        for locale in (LOCALE_EN, LOCALE_IT):
            names["series_name"][locale.language] = series.get_display_name(locale)
            values["series_name"][locale.language] = series.identifier

            names["processing_method"][
                locale.language
            ] = static.CoverageTimeSeriesProcessingMethod.get_param_display_name(locale)
            values["processing_method"][
                locale.language
            ] = series.processing_method.get_value_display_name(locale)

            names["series_configuration"][
                locale.language
            ] = series.overview_series.configuration.get_display_name(locale)
            values["series_configuration"][
                locale.language
            ] = series.overview_series.configuration.identifier

            names["climatological_variable"][
                locale.language
            ] = series.overview_series.configuration.climatic_indicator.get_display_name(
                locale
            )
            values["climatological_variable"][locale.language] = {
                LOCALE_EN: series.overview_series.configuration.climatic_indicator.display_name_english,
                LOCALE_IT: series.overview_series.configuration.climatic_indicator.display_name_italian,
            }.get(
                locale,
                series.overview_series.configuration.climatic_indicator.identifier,
            )

            names["measure"][
                locale.language
            ] = static.MeasureType.get_param_display_name(locale)
            values["measure"][
                locale.language
            ] = series.overview_series.configuration.climatic_indicator.measure_type.get_value_display_name(
                locale
            )

            names["aggregation_period"][
                locale.language
            ] = static.AggregationPeriod.get_param_display_name(locale)
            values["aggregation_period"][
                locale.language
            ] = series.overview_series.configuration.climatic_indicator.aggregation_period.get_value_display_name(
                locale
            )

        return cls(parameter_names=names, parameter_values=values)


class LegacyTimeSeries(pydantic.BaseModel):
    name: str
    values: list[TimeSeriesItem]
    info: typing.Optional[dict[str, str | int | float | bool | dict]] = None
    translations: typing.Optional[LegacyTimeSeriesTranslations] = None

    @classmethod
    def from_observation_station_data_series(
        cls, series: "dataseries.ObservationStationDataSeries"
    ):
        return cls(
            name=series.identifier,
            values=[
                TimeSeriesItem(datetime=timestamp, value=value)
                for timestamp, value in series.data_.to_dict().items()
                if not math.isnan(value)
            ],
            info={
                "processing_method": series.processing_method.value,
                "station": series.observation_station.name,
                "variable": series.observation_series_configuration.climatic_indicator.name,
                "series_elaboration": None,
                "derived_series": None,
            },
            translations=(
                LegacyTimeSeriesTranslations.from_observation_station_data_series(
                    series
                )
            ),
        )

    @classmethod
    def from_forecast_data_series(cls, series: "dataseries.ForecastDataSeries"):
        return cls(
            name=series.identifier,
            values=[
                TimeSeriesItem(datetime=timestamp, value=value)
                for timestamp, value in series.data_.to_dict().items()
                if not math.isnan(value)
            ],
            info={
                "processing_method": series.processing_method.value,
                "coverage_identifier": series.forecast_coverage.identifier,
                "coverage_configuration": (
                    series.forecast_coverage.configuration.identifier
                ),
                "aggregation_period": (
                    series.forecast_coverage.configuration.climatic_indicator.aggregation_period.value
                ),
                "climatological_model": series.forecast_coverage.forecast_model.name,
                "climatological_variable": (
                    series.forecast_coverage.configuration.climatic_indicator.name
                ),
                "measure": (
                    series.forecast_coverage.configuration.climatic_indicator.measure_type.value
                ),
                "scenario": series.forecast_coverage.scenario.value,
                "year_period": series.forecast_coverage.year_period.value,
            },
            translations=LegacyTimeSeriesTranslations.from_forecast_data_series(series),
        )

    @classmethod
    def from_forecast_overview_series(
        cls, series: "dataseries.ForecastOverviewDataSeries"
    ):
        info = {
            "series_configuration": series.overview_series.configuration.identifier,
            "climatic_indicator": series.overview_series.configuration.climatic_indicator.identifier,
            "processing_method": legacy.CoverageDataSmoothingStrategy.from_processing_method(
                series.processing_method
            ).value,
            "coverage_identifier": series.overview_series.identifier,
            "coverage_configuration": series.overview_series.configuration.identifier,
            "archive": "barometro_climatico",
            "climatological_variable": series.overview_series.configuration.climatic_indicator.name,
            "scenario": series.overview_series.scenario.value,
        }
        if series.dataset_type in (
            static.DatasetType.LOWER_UNCERTAINTY,
            static.DatasetType.UPPER_UNCERTAINTY,
        ):
            info["uncertainty_type"] = (
                legacy.convert_to_uncertainty_type(series.dataset_type) or ""
            )
        return cls(
            name=series.identifier,
            values=[
                TimeSeriesItem(datetime=timestamp, value=value)
                for timestamp, value in series.data_.to_dict().items()
                if not math.isnan(value)
            ],
            info=info,
            translations=LegacyTimeSeriesTranslations.from_forecast_overview_data_series(
                series
            ),
        )

    @classmethod
    def from_historical_overview_series(
        cls, series: "dataseries.ObservationOverviewDataSeries"
    ):
        info = {
            "series_configuration": series.overview_series.configuration.identifier,
            "climatic_indicator": series.overview_series.configuration.climatic_indicator.identifier,
            "processing_method": legacy.CoverageDataSmoothingStrategy.from_processing_method(
                series.processing_method
            ).value,
            "coverage_identifier": series.overview_series.identifier,
            "coverage_configuration": series.overview_series.configuration.identifier,
            "archive": "barometro_climatico",
            "historical_variable": legacy.convert_overview_historical_variable(
                series.overview_series.configuration.climatic_indicator
            ),
        }
        return cls(
            name=series.identifier,
            values=[
                TimeSeriesItem(datetime=timestamp, value=value)
                for timestamp, value in series.data_.to_dict().items()
                if not math.isnan(value)
            ],
            info=info,
            translations=LegacyTimeSeriesTranslations.from_historical_overview_data_series(
                series
            ),
        )


class LegacyTimeSeriesList(pydantic.BaseModel):
    series: list[LegacyTimeSeries]
