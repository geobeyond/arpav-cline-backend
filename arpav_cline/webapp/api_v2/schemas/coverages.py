import typing
from typing import Optional

import pydantic

from fastapi import Request

from ....config import (
    ArpavPpcvSettings,
    LOCALE_EN,
    LOCALE_IT,
)
from ....schemas.coverages import (
    ConfigurationParameter,
    ForecastCoverageConfiguration,
    ForecastCoverageInternal,
    HistoricalCoverageConfiguration,
    HistoricalCoverageInternal,
)
from ....schemas.static import (
    DatasetType,
    ForecastScenario,
    ForecastYearPeriod,
    HistoricalDecade,
    HistoricalYearPeriod,
    HistoricalReferencePeriod,
)
from .base import (
    ListLinks,
    ListMeta,
    WebResourceList,
    get_meta,
    get_list_links,
    get_pagination_urls,
)


class ImageLegendColor(pydantic.BaseModel):
    value: float
    color: str


class CoverageImageLegend(pydantic.BaseModel):
    color_entries: list[ImageLegendColor]


class ConfigurationParameterValueEmbeddedInConfigurationParameter(pydantic.BaseModel):
    name: str
    display_name_english: str
    display_name_italian: str
    description_english: str | None
    description_italian: str | None
    sort_order: int


class ConfigurationParameterReadListItem(pydantic.BaseModel):
    name: str
    display_name_english: str
    display_name_italian: str
    description_english: str | None
    description_italian: str | None
    allowed_values: list[ConfigurationParameterValueEmbeddedInConfigurationParameter]

    @classmethod
    def from_db_instance(
        cls,
        instance: ConfigurationParameter,
        request: Request,
    ):
        return cls(
            **instance.model_dump(
                exclude={
                    "display_name_english",
                    "display_name_italian",
                }
            ),
            display_name_english=instance.display_name_english or instance.name,
            display_name_italian=instance.display_name_italian or instance.name,
            allowed_values=[
                ConfigurationParameterValueEmbeddedInConfigurationParameter(
                    **pv.model_dump(
                        exclude={
                            "display_name_english",
                            "display_name_italian",
                            "sort_order",
                        }
                    ),
                    display_name_english=pv.display_name_english or pv.name,
                    display_name_italian=pv.display_name_italian or pv.name,
                    sort_order=pv.sort_order or 0,
                )
                for pv in instance.allowed_values
            ],
        )


class ConfigurationParameterPossibleValueRead(pydantic.BaseModel):
    configuration_parameter_name: str
    configuration_parameter_display_name_english: str
    configuration_parameter_display_name_italian: str
    configuration_parameter_value: str


class LegacyHistoricalCoverageConfigurationReadListItem(pydantic.BaseModel):
    url: pydantic.AnyHttpUrl
    identifier: str
    name: str
    display_name_english: str
    display_name_italian: str
    wms_main_layer_name: str | None
    climatic_indicator_identifier: str
    reference_period: HistoricalReferencePeriod | None
    decades: list[HistoricalDecade]
    year_periods: list[HistoricalYearPeriod]
    possible_values: list[ConfigurationParameterPossibleValueRead]

    @classmethod
    def from_db_instance(
        cls,
        instance: HistoricalCoverageConfiguration,
        request: Request,
    ) -> "LegacyHistoricalCoverageConfigurationReadListItem":
        url = request.url_for(
            "legacy_get_coverage_configuration",
            **{"coverage_configuration_identifier": instance.identifier},
        )
        return cls(
            **instance.model_dump(
                exclude={
                    "display_name_english",
                    "display_name_italian",
                    "decades",
                }
            ),
            name=instance.identifier,
            decades=instance.decades or [],
            climatic_indicator_identifier=instance.climatic_indicator.identifier,
            display_name_english=instance.climatic_indicator.display_name_english,
            display_name_italian=instance.climatic_indicator.display_name_italian,
            url=str(url),
            year_periods=[yp.value for yp in instance.year_period_group.year_periods],
            possible_values=cls.prepare_possible_values(instance),
        )

    @classmethod
    def prepare_possible_values(
        cls, instance: HistoricalCoverageConfiguration
    ) -> list[ConfigurationParameterPossibleValueRead]:
        possible_values = [
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="aggregation_period",
                configuration_parameter_display_name_english=instance.climatic_indicator.aggregation_period.get_param_display_name(
                    LOCALE_EN
                ),
                configuration_parameter_display_name_italian=instance.climatic_indicator.aggregation_period.get_param_display_name(
                    LOCALE_IT
                ),
                configuration_parameter_value=instance.climatic_indicator.aggregation_period.value,
            ),
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="climatological_variable",
                configuration_parameter_display_name_english=instance.climatic_indicator.display_name_english,
                configuration_parameter_display_name_italian=instance.climatic_indicator.display_name_italian,
                configuration_parameter_value=instance.climatic_indicator.name,
            ),
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="measure",
                configuration_parameter_display_name_english=instance.climatic_indicator.measure_type.get_param_display_name(
                    LOCALE_EN
                ),
                configuration_parameter_display_name_italian=instance.climatic_indicator.measure_type.get_param_display_name(
                    LOCALE_IT
                ),
                configuration_parameter_value=instance.climatic_indicator.measure_type.value,
            ),
        ]
        if instance.reference_period is not None:
            possible_values.append(
                ConfigurationParameterPossibleValueRead(
                    configuration_parameter_name="reference_period",
                    configuration_parameter_display_name_english=instance.reference_period.get_param_display_name(
                        LOCALE_EN
                    ),
                    configuration_parameter_display_name_italian=instance.reference_period.get_param_display_name(
                        LOCALE_IT
                    ),
                    configuration_parameter_value=instance.reference_period.value,
                ),
            )
        for decade in instance.decades or []:
            possible_values.append(
                ConfigurationParameterPossibleValueRead(
                    configuration_parameter_name="decade",
                    configuration_parameter_display_name_english=decade.get_param_display_name(
                        LOCALE_EN
                    ),
                    configuration_parameter_display_name_italian=decade.get_param_display_name(
                        LOCALE_IT
                    ),
                    configuration_parameter_value=decade.value,
                ),
            )
        for year_period in instance.year_period_group.year_periods:
            possible_values.append(
                ConfigurationParameterPossibleValueRead(
                    configuration_parameter_name="year_period",
                    configuration_parameter_display_name_english=year_period.get_param_display_name(
                        LOCALE_EN
                    ),
                    configuration_parameter_display_name_italian=year_period.get_param_display_name(
                        LOCALE_IT
                    ),
                    configuration_parameter_value=year_period.value,
                ),
            )
        return possible_values


class LegacyHistoricalCoverageReadListItem(pydantic.BaseModel):
    url: pydantic.AnyHttpUrl
    identifier: str
    name: str
    related_coverage_configuration_url: pydantic.AnyHttpUrl
    display_name_english: str
    display_name_italian: str
    wms_base_url: str
    possible_values: list[ConfigurationParameterPossibleValueRead]

    @classmethod
    def from_db_instance(
        cls,
        instance: HistoricalCoverageInternal,
        request: Request,
    ) -> "LegacyHistoricalCoverageReadListItem":
        url = request.url_for(
            "legacy_get_coverage",
            **{"coverage_identifier": instance.identifier},
        )
        return cls(
            url=str(url),
            identifier=instance.identifier,
            name=instance.identifier,
            related_coverage_configuration_url=str(
                request.url_for(
                    "legacy_get_coverage_configuration",
                    coverage_configuration_identifier=instance.configuration.identifier,
                )
            ),
            display_name_english=instance.configuration.climatic_indicator.display_name_english,
            display_name_italian=instance.configuration.climatic_indicator.display_name_italian,
            wms_base_url=str(
                request.url_for("wms_endpoint", coverage_identifier=instance.identifier)
            ),
            possible_values=cls.prepare_possible_values(instance),
        )

    @classmethod
    def prepare_possible_values(
        cls, instance: HistoricalCoverageInternal
    ) -> list[ConfigurationParameterPossibleValueRead]:
        possible_values = [
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="aggregation_period",
                configuration_parameter_display_name_english=instance.configuration.climatic_indicator.aggregation_period.get_param_display_name(
                    LOCALE_EN
                ),
                configuration_parameter_display_name_italian=instance.configuration.climatic_indicator.aggregation_period.get_param_display_name(
                    LOCALE_IT
                ),
                configuration_parameter_value=instance.configuration.climatic_indicator.aggregation_period.value,
            ),
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="climatological_variable",
                configuration_parameter_display_name_english=instance.configuration.climatic_indicator.display_name_english,
                configuration_parameter_display_name_italian=instance.configuration.climatic_indicator.display_name_italian,
                configuration_parameter_value=instance.configuration.climatic_indicator.name,
            ),
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="measure",
                configuration_parameter_display_name_english=instance.configuration.climatic_indicator.measure_type.get_param_display_name(
                    LOCALE_EN
                ),
                configuration_parameter_display_name_italian=instance.configuration.climatic_indicator.measure_type.get_param_display_name(
                    LOCALE_IT
                ),
                configuration_parameter_value=instance.configuration.climatic_indicator.measure_type.value,
            ),
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="year_period",
                configuration_parameter_display_name_english=instance.year_period.get_param_display_name(
                    LOCALE_EN
                ),
                configuration_parameter_display_name_italian=instance.year_period.get_param_display_name(
                    LOCALE_IT
                ),
                configuration_parameter_value=instance.year_period.value,
            ),
        ]
        if instance.configuration.reference_period is not None:
            possible_values.append(
                ConfigurationParameterPossibleValueRead(
                    configuration_parameter_name="reference_period",
                    configuration_parameter_display_name_english=instance.configuration.reference_period.get_param_display_name(
                        LOCALE_EN
                    ),
                    configuration_parameter_display_name_italian=instance.configuration.reference_period.get_param_display_name(
                        LOCALE_IT
                    ),
                    configuration_parameter_value=instance.configuration.reference_period.value,
                ),
            )
        if instance.decade is not None:
            possible_values.append(
                ConfigurationParameterPossibleValueRead(
                    configuration_parameter_name="decade",
                    configuration_parameter_display_name_english=instance.decade.get_param_display_name(
                        LOCALE_EN
                    ),
                    configuration_parameter_display_name_italian=instance.decade.get_param_display_name(
                        LOCALE_IT
                    ),
                    configuration_parameter_value=instance.decade.value,
                ),
            )
        return possible_values


class ForecastCoverageEmbeddedInConfiguration(pydantic.BaseModel):
    identifier: str
    url: pydantic.AnyHttpUrl

    @classmethod
    def from_instance(
        cls,
        instance: ForecastCoverageInternal,
        request: Request,
    ) -> "ForecastCoverageEmbeddedInConfiguration":
        return cls(
            identifier=instance.identifier,
            url=str(
                request.url_for(
                    "legacy_get_coverage", coverage_identifier=instance.identifier
                )
            ),
        )


class HistoricalCoverageEmbeddedInConfiguration(pydantic.BaseModel):
    identifier: str
    url: pydantic.AnyHttpUrl

    @classmethod
    def from_instance(
        cls,
        instance: HistoricalCoverageInternal,
        request: Request,
    ) -> "HistoricalCoverageEmbeddedInConfiguration":
        return cls(
            identifier=instance.identifier,
            url=str(
                request.url_for(
                    "legacy_get_coverage", coverage_identifier=instance.identifier
                )
            ),
        )


class LegacyHistoricalCoverageConfigurationReadDetail(
    LegacyHistoricalCoverageConfigurationReadListItem
):
    url: pydantic.AnyHttpUrl
    unit_english: str
    unit_italian: str
    allowed_coverage_identifiers: list[HistoricalCoverageEmbeddedInConfiguration]
    description_english: str | None
    description_italian: str | None
    legend: CoverageImageLegend
    data_precision: int

    @classmethod
    def from_db_instance(  # noqa
        cls,
        instance: HistoricalCoverageConfiguration,
        historical_coverages: list[HistoricalCoverageInternal],
        legend_colors: list[tuple[float, str]],
        request: Request,
    ) -> "LegacyHistoricalCoverageConfigurationReadDetail":
        url = request.url_for(
            "legacy_get_coverage_configuration",
            coverage_configuration_identifier=instance.identifier,
        )
        return cls(
            **instance.model_dump(
                exclude={
                    "display_name_english",
                    "display_name_italian",
                    "decades",
                }
            ),
            name=instance.identifier,
            decades=instance.decades or [],
            climatic_indicator_identifier=instance.climatic_indicator.identifier,
            display_name_english=instance.climatic_indicator.display_name_english,
            display_name_italian=instance.climatic_indicator.display_name_italian,
            description_english=instance.climatic_indicator.description_english,
            description_italian=instance.climatic_indicator.description_italian,
            unit_english=instance.climatic_indicator.unit_english,
            unit_italian=instance.climatic_indicator.unit_italian,
            data_precision=instance.climatic_indicator.data_precision,
            url=str(url),
            possible_values=cls.prepare_possible_values(instance),
            allowed_coverage_identifiers=[
                HistoricalCoverageEmbeddedInConfiguration.from_instance(i, request)
                for i in historical_coverages
            ],
            legend=CoverageImageLegend(
                color_entries=[
                    ImageLegendColor(value=v, color=c) for v, c in legend_colors
                ]
            ),
        )


class LegacyForecastCoverageConfigurationReadListItem(pydantic.BaseModel):
    url: pydantic.AnyHttpUrl
    identifier: str
    name: str
    display_name_english: str
    display_name_italian: str
    wms_main_layer_name: str | None
    wms_secondary_layer_name: str | None
    climatic_indicator_identifier: str
    forecast_model_names: list[str]
    scenarios: list[ForecastScenario]
    has_associated_uncertainty_datasets: bool
    year_periods: list[ForecastYearPeriod]
    possible_values: list[ConfigurationParameterPossibleValueRead]

    @classmethod
    def from_db_instance(
        cls,
        instance: ForecastCoverageConfiguration,
        request: Request,
    ) -> "LegacyForecastCoverageConfigurationReadListItem":
        url = request.url_for(
            "legacy_get_coverage_configuration",
            **{"coverage_configuration_identifier": instance.identifier},
        )
        return cls(
            **instance.model_dump(
                exclude={
                    "display_name_english",
                    "display_name_italian",
                }
            ),
            name=instance.identifier,
            climatic_indicator_identifier=instance.climatic_indicator.identifier,
            forecast_model_names=[
                fml.forecast_model.name
                for fml in instance.forecast_model_group.forecast_model_links
            ],
            year_periods=[yp.value for yp in instance.year_period_group.year_periods],
            has_associated_uncertainty_datasets=(
                instance.lower_uncertainty_netcdf_main_dataset_name is not None
            ),
            display_name_english=instance.climatic_indicator.display_name_english,
            display_name_italian=instance.climatic_indicator.display_name_italian,
            url=str(url),
            possible_values=cls.prepare_possible_values(instance),
        )

    @classmethod
    def prepare_possible_values(
        cls, instance: ForecastCoverageConfiguration
    ) -> list[ConfigurationParameterPossibleValueRead]:
        possible_values = [
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="aggregation_period",
                configuration_parameter_display_name_english=instance.climatic_indicator.aggregation_period.get_param_display_name(
                    LOCALE_EN
                ),
                configuration_parameter_display_name_italian=instance.climatic_indicator.aggregation_period.get_param_display_name(
                    LOCALE_IT
                ),
                configuration_parameter_value=instance.climatic_indicator.aggregation_period.value,
            ),
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="climatological_variable",
                configuration_parameter_display_name_english=instance.climatic_indicator.display_name_english,
                configuration_parameter_display_name_italian=instance.climatic_indicator.display_name_italian,
                configuration_parameter_value=instance.climatic_indicator.name,
            ),
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="measure",
                configuration_parameter_display_name_english=instance.climatic_indicator.measure_type.get_param_display_name(
                    LOCALE_EN
                ),
                configuration_parameter_display_name_italian=instance.climatic_indicator.measure_type.get_param_display_name(
                    LOCALE_IT
                ),
                configuration_parameter_value=instance.climatic_indicator.measure_type.value,
            ),
        ]
        for forecast_model_link in instance.forecast_model_group.forecast_model_links:
            possible_values.append(
                ConfigurationParameterPossibleValueRead(
                    configuration_parameter_name="climatological_model",
                    configuration_parameter_display_name_english=forecast_model_link.forecast_model.display_name_english,
                    configuration_parameter_display_name_italian=forecast_model_link.forecast_model.display_name_italian,
                    configuration_parameter_value=forecast_model_link.forecast_model.name,
                ),
            )
        for scenario in instance.scenarios:
            possible_values.append(
                ConfigurationParameterPossibleValueRead(
                    configuration_parameter_name="scenario",
                    configuration_parameter_display_name_english=scenario.get_param_display_name(
                        LOCALE_EN
                    ),
                    configuration_parameter_display_name_italian=scenario.get_param_display_name(
                        LOCALE_IT
                    ),
                    configuration_parameter_value=scenario.value,
                ),
            )
        if instance.lower_uncertainty_thredds_url_pattern is not None:
            type_ = DatasetType.LOWER_UNCERTAINTY
            possible_values.append(
                ConfigurationParameterPossibleValueRead(
                    configuration_parameter_name="uncertainty_type",
                    configuration_parameter_display_name_english=type_.get_param_display_name(
                        LOCALE_EN
                    ),
                    configuration_parameter_display_name_italian=type_.get_param_display_name(
                        LOCALE_IT
                    ),
                    configuration_parameter_value=type_.value,
                ),
            )
        if instance.upper_uncertainty_thredds_url_pattern is not None:
            type_ = DatasetType.UPPER_UNCERTAINTY
            possible_values.append(
                ConfigurationParameterPossibleValueRead(
                    configuration_parameter_name="uncertainty_type",
                    configuration_parameter_display_name_english=type_.get_param_display_name(
                        LOCALE_EN
                    ),
                    configuration_parameter_display_name_italian=type_.get_param_display_name(
                        LOCALE_IT
                    ),
                    configuration_parameter_value=type_.value,
                ),
            )
        for time_window_link in instance.forecast_time_window_links:
            possible_values.append(
                ConfigurationParameterPossibleValueRead(
                    configuration_parameter_name="time_window",
                    configuration_parameter_display_name_english=time_window_link.forecast_time_window.display_name_english,
                    configuration_parameter_display_name_italian=time_window_link.forecast_time_window.display_name_italian,
                    configuration_parameter_value=time_window_link.forecast_time_window.name,
                ),
            )
        for year_period in instance.year_period_group.year_periods:
            possible_values.append(
                ConfigurationParameterPossibleValueRead(
                    configuration_parameter_name="year_period",
                    configuration_parameter_display_name_english=year_period.get_param_display_name(
                        LOCALE_EN
                    ),
                    configuration_parameter_display_name_italian=year_period.get_param_display_name(
                        LOCALE_IT
                    ),
                    configuration_parameter_value=year_period.value,
                ),
            )
        return possible_values


class LegacyForecastCoverageConfigurationReadDetail(
    LegacyForecastCoverageConfigurationReadListItem
):
    url: pydantic.AnyHttpUrl
    unit_english: str
    unit_italian: str
    allowed_coverage_identifiers: list[ForecastCoverageEmbeddedInConfiguration]
    description_english: str | None
    description_italian: str | None
    legend: CoverageImageLegend
    data_precision: int

    @classmethod
    def from_db_instance(
        cls,
        instance: ForecastCoverageConfiguration,
        forecast_coverages: list[ForecastCoverageInternal],
        legend_colors: list[tuple[float, str]],
        request: Request,
    ) -> "LegacyForecastCoverageConfigurationReadDetail":
        url = request.url_for(
            "legacy_get_coverage_configuration",
            **{"coverage_configuration_identifier": instance.identifier},
        )
        return cls(
            **instance.model_dump(),
            name=instance.identifier,
            climatic_indicator_identifier=instance.climatic_indicator.identifier,
            forecast_model_names=[
                fml.forecast_model.name
                for fml in instance.forecast_model_group.forecast_model_links
            ],
            year_periods=[yp.value for yp in instance.year_period_group.year_periods],
            has_associated_uncertainty_datasets=(
                instance.lower_uncertainty_netcdf_main_dataset_name is not None
            ),
            display_name_english=instance.climatic_indicator.display_name_english,
            display_name_italian=instance.climatic_indicator.display_name_italian,
            description_english=instance.climatic_indicator.description_english,
            description_italian=instance.climatic_indicator.description_italian,
            unit_english=instance.climatic_indicator.unit_english,
            unit_italian=instance.climatic_indicator.unit_italian,
            data_precision=instance.climatic_indicator.data_precision,
            url=str(url),
            possible_values=cls.prepare_possible_values(instance),
            allowed_coverage_identifiers=[
                ForecastCoverageEmbeddedInConfiguration.from_instance(i, request)
                for i in forecast_coverages
            ],
            legend=CoverageImageLegend(
                color_entries=[
                    ImageLegendColor(value=v, color=c) for v, c in legend_colors
                ]
            ),
        )


class LegacyCoverageConfigurationList(pydantic.BaseModel):
    items: list[
        typing.Union[
            LegacyForecastCoverageConfigurationReadListItem,
            LegacyHistoricalCoverageConfigurationReadListItem,
        ]
    ]
    meta: ListMeta
    links: ListLinks
    path_operation_name: typing.ClassVar[str] = "legacy_list_coverage_configurations"

    @classmethod
    def from_items(
        cls,
        forecast_coverage_configurations: typing.Sequence[
            ForecastCoverageConfiguration
        ],
        historical_coverage_configurations: typing.Sequence[
            HistoricalCoverageConfiguration
        ],
        request: Request,
        *,
        limit: int,
        offset: int,
        unfiltered_total_forecast_coverage_configurations: int,
        unfiltered_total_historical_coverage_configurations: int,
    ):
        all_items: list[
            typing.Union[
                LegacyForecastCoverageConfigurationReadListItem,
                LegacyHistoricalCoverageConfigurationReadListItem,
            ]
        ] = [
            LegacyForecastCoverageConfigurationReadListItem.from_db_instance(i, request)
            for i in forecast_coverage_configurations
        ]
        all_items.extend(
            [
                LegacyHistoricalCoverageConfigurationReadListItem.from_db_instance(
                    i, request
                )
                for i in historical_coverage_configurations
            ]
        )
        relevant = all_items[offset : offset + limit]
        filtered_total = len(forecast_coverage_configurations) + len(
            historical_coverage_configurations
        )

        return cls(
            meta=get_meta(
                num_returned_records=len(relevant),
                unfiltered_total=(
                    unfiltered_total_forecast_coverage_configurations
                    + unfiltered_total_historical_coverage_configurations
                ),
                filtered_total=filtered_total,
            ),
            links=get_list_links(
                request,
                cls.path_operation_name,
                limit,
                offset,
                filtered_total,
                len(relevant),
            ),
            items=relevant,
        )


class LegacyForecastCoverageReadListItem(pydantic.BaseModel):
    url: pydantic.AnyHttpUrl
    identifier: str
    name: str
    related_coverage_configuration_url: pydantic.AnyHttpUrl
    display_name_english: str
    display_name_italian: str
    wms_base_url: str
    wms_main_layer_name: str | None = None
    wms_secondary_layer_name: str | None = None
    possible_values: list[ConfigurationParameterPossibleValueRead]

    @classmethod
    def from_db_instance(
        cls,
        instance: ForecastCoverageInternal,
        request: Request,
    ) -> "LegacyForecastCoverageReadListItem":
        wms_base_url = request.url_for(
            "wms_endpoint", coverage_identifier=instance.identifier
        )
        return cls(
            url=str(
                request.url_for(
                    "legacy_get_coverage",
                    coverage_identifier=instance.identifier,
                )
            ),
            identifier=instance.identifier,
            name=instance.identifier,
            wms_base_url=str(wms_base_url),
            display_name_english=instance.configuration.climatic_indicator.display_name_english,
            display_name_italian=instance.configuration.climatic_indicator.display_name_italian,
            wms_main_layer_name=(
                instance.get_wms_main_layer_name()
                if instance.configuration.wms_main_layer_name is not None
                else None
            ),
            wms_secondary_layer_name=(
                instance.get_wms_secondary_layer_name()
                if instance.configuration.wms_secondary_layer_name is not None
                else None
            ),
            related_coverage_configuration_url=str(
                request.url_for(
                    "legacy_get_coverage_configuration",
                    coverage_configuration_identifier=instance.configuration.identifier,
                )
            ),
            possible_values=cls.prepare_possible_values(instance),
        )

    @classmethod
    def prepare_possible_values(
        cls, instance: ForecastCoverageInternal
    ) -> list[ConfigurationParameterPossibleValueRead]:
        possible_values = [
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="aggregation_period",
                configuration_parameter_display_name_english=(
                    instance.configuration.climatic_indicator.aggregation_period.get_param_display_name(
                        LOCALE_EN
                    )
                ),
                configuration_parameter_display_name_italian=(
                    instance.configuration.climatic_indicator.aggregation_period.get_param_display_name(
                        LOCALE_IT
                    )
                ),
                configuration_parameter_value=(
                    instance.configuration.climatic_indicator.aggregation_period.value
                ),
            ),
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="climatological_variable",
                configuration_parameter_display_name_english=(
                    instance.configuration.climatic_indicator.display_name_english
                ),
                configuration_parameter_display_name_italian=(
                    instance.configuration.climatic_indicator.display_name_italian
                ),
                configuration_parameter_value=(
                    instance.configuration.climatic_indicator.name
                ),
            ),
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="measure",
                configuration_parameter_display_name_english=(
                    instance.configuration.climatic_indicator.measure_type.get_param_display_name(
                        LOCALE_EN
                    )
                ),
                configuration_parameter_display_name_italian=(
                    instance.configuration.climatic_indicator.measure_type.get_param_display_name(
                        LOCALE_IT
                    )
                ),
                configuration_parameter_value=(
                    instance.configuration.climatic_indicator.measure_type.value
                ),
            ),
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="climatological_model",
                configuration_parameter_display_name_english=instance.forecast_model.display_name_english,
                configuration_parameter_display_name_italian=instance.forecast_model.display_name_italian,
                configuration_parameter_value=instance.forecast_model.name,
            ),
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="scenario",
                configuration_parameter_display_name_english=instance.scenario.get_param_display_name(
                    LOCALE_EN
                ),
                configuration_parameter_display_name_italian=instance.scenario.get_param_display_name(
                    LOCALE_IT
                ),
                configuration_parameter_value=instance.scenario.value,
            ),
        ]
        if instance.configuration.lower_uncertainty_thredds_url_pattern is not None:
            type_ = DatasetType.LOWER_UNCERTAINTY
            possible_values.append(
                ConfigurationParameterPossibleValueRead(
                    configuration_parameter_name="uncertainty_type",
                    configuration_parameter_display_name_english=type_.get_param_display_name(
                        LOCALE_EN
                    ),
                    configuration_parameter_display_name_italian=type_.get_param_display_name(
                        LOCALE_IT
                    ),
                    configuration_parameter_value=type_.value,
                ),
            )
        if instance.configuration.upper_uncertainty_thredds_url_pattern is not None:
            type_ = DatasetType.UPPER_UNCERTAINTY
            possible_values.append(
                ConfigurationParameterPossibleValueRead(
                    configuration_parameter_name="uncertainty_type",
                    configuration_parameter_display_name_english=type_.get_param_display_name(
                        LOCALE_EN
                    ),
                    configuration_parameter_display_name_italian=type_.get_param_display_name(
                        LOCALE_IT
                    ),
                    configuration_parameter_value=type_.value,
                ),
            )
        if instance.forecast_time_window is not None:
            possible_values.append(
                ConfigurationParameterPossibleValueRead(
                    configuration_parameter_name="time_window",
                    configuration_parameter_display_name_english=instance.forecast_time_window.display_name_english,
                    configuration_parameter_display_name_italian=instance.forecast_time_window.display_name_italian,
                    configuration_parameter_value=instance.forecast_time_window.name,
                ),
            )

        possible_values.append(
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="year_period",
                configuration_parameter_display_name_english=instance.year_period.get_param_display_name(
                    LOCALE_EN
                ),
                configuration_parameter_display_name_italian=instance.year_period.get_param_display_name(
                    LOCALE_IT
                ),
                configuration_parameter_value=instance.year_period.value,
            ),
        )
        return possible_values


class LegacyForecastCoverageReadDetail(pydantic.BaseModel):
    data_precision: int
    description_english: str | None
    description_italian: str | None
    display_name_english: str
    display_name_italian: str
    file_download_url: pydantic.AnyHttpUrl
    forecast_model: str
    identifier: str
    legend: CoverageImageLegend
    observation_stations_vector_tile_layer_url: str | None = None
    possible_values: list[ConfigurationParameterPossibleValueRead]
    related_coverage_configuration_url: str
    climatic_indicator_url: str
    scenario: ForecastScenario
    time_window: Optional[str] = None
    unit_english: str
    unit_italian: str
    url: pydantic.AnyHttpUrl
    wms_base_url: pydantic.AnyHttpUrl
    wms_main_layer_name: str | None = None
    wms_secondary_layer_name: str | None = None
    year_period: ForecastYearPeriod

    @classmethod
    def from_db_instance(
        cls,
        instance: ForecastCoverageInternal,
        request: Request,
        settings: ArpavPpcvSettings,
        legend_colors: list[tuple[float, str]],
    ) -> "LegacyForecastCoverageReadDetail":
        vector_tile_stations_url = None
        if len(instance.configuration.observation_series_configuration_links) > 0:
            vector_tile_stations_url = instance.configuration.observation_series_configuration_links[
                0
            ].observation_series_configuration.get_observation_stations_vector_tile_layer_url(
                settings
            )
        return cls(
            url=str(
                request.url_for(
                    "legacy_get_coverage", coverage_identifier=instance.identifier
                )
            ),
            identifier=instance.identifier,
            related_coverage_configuration_url=str(
                request.url_for(
                    "legacy_get_coverage_configuration",
                    coverage_configuration_identifier=instance.configuration.identifier,
                )
            ),
            climatic_indicator_url=str(
                request.url_for(
                    "get_climatic_indicator",
                    climatic_indicator_identifier=instance.configuration.climatic_indicator.identifier,
                ),
            ),
            wms_base_url=str(
                request.url_for("wms_endpoint", coverage_identifier=instance.identifier)
            ),
            forecast_model=instance.forecast_model.name,
            scenario=instance.scenario.value,
            year_period=instance.year_period.value,
            time_window=(
                instance.forecast_time_window.name
                if instance.forecast_time_window is not None
                else None
            ),
            file_download_url=str(
                request.url_for(
                    "get_forecast_data", coverage_identifier=instance.identifier
                )
            ),
            wms_main_layer_name=instance.get_wms_main_layer_name(),
            wms_secondary_layer_name=(
                instance.get_wms_secondary_layer_name()
                if instance.configuration.wms_secondary_layer_name
                else None
            ),
            possible_values=cls.prepare_possible_values(instance),
            observation_stations_vector_tile_layer_url=vector_tile_stations_url,
            display_name_english=instance.configuration.climatic_indicator.display_name_english,
            display_name_italian=instance.configuration.climatic_indicator.display_name_italian,
            description_english=instance.configuration.climatic_indicator.description_english,
            description_italian=instance.configuration.climatic_indicator.description_italian,
            unit_english=instance.configuration.climatic_indicator.unit_english,
            unit_italian=instance.configuration.climatic_indicator.unit_italian,
            data_precision=instance.configuration.climatic_indicator.data_precision,
            legend=CoverageImageLegend(
                color_entries=[
                    ImageLegendColor(value=v, color=c) for v, c in legend_colors
                ]
            ),
        )

    @classmethod
    def prepare_possible_values(
        cls, instance: ForecastCoverageInternal
    ) -> list[ConfigurationParameterPossibleValueRead]:
        possible_values = [
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="aggregation_period",
                configuration_parameter_display_name_english=(
                    instance.configuration.climatic_indicator.aggregation_period.get_param_display_name(
                        LOCALE_EN
                    )
                ),
                configuration_parameter_display_name_italian=(
                    instance.configuration.climatic_indicator.aggregation_period.get_param_display_name(
                        LOCALE_IT
                    )
                ),
                configuration_parameter_value=(
                    instance.configuration.climatic_indicator.aggregation_period.value
                ),
            ),
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="climatological_variable",
                configuration_parameter_display_name_english=(
                    instance.configuration.climatic_indicator.display_name_english
                ),
                configuration_parameter_display_name_italian=(
                    instance.configuration.climatic_indicator.display_name_italian
                ),
                configuration_parameter_value=(
                    instance.configuration.climatic_indicator.name
                ),
            ),
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="measure",
                configuration_parameter_display_name_english=instance.configuration.climatic_indicator.measure_type.get_param_display_name(
                    LOCALE_EN
                ),
                configuration_parameter_display_name_italian=instance.configuration.climatic_indicator.measure_type.get_param_display_name(
                    LOCALE_IT
                ),
                configuration_parameter_value=instance.configuration.climatic_indicator.measure_type.value,
            ),
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="climatological_model",
                configuration_parameter_display_name_english=instance.forecast_model.display_name_english,
                configuration_parameter_display_name_italian=instance.forecast_model.display_name_italian,
                configuration_parameter_value=instance.forecast_model.name,
            ),
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="scenario",
                configuration_parameter_display_name_english=instance.scenario.get_param_display_name(
                    LOCALE_EN
                ),
                configuration_parameter_display_name_italian=instance.scenario.get_param_display_name(
                    LOCALE_IT
                ),
                configuration_parameter_value=instance.scenario.value,
            ),
            ConfigurationParameterPossibleValueRead(
                configuration_parameter_name="year_period",
                configuration_parameter_display_name_english=instance.year_period.get_param_display_name(
                    LOCALE_EN
                ),
                configuration_parameter_display_name_italian=instance.year_period.get_param_display_name(
                    LOCALE_IT
                ),
                configuration_parameter_value=instance.year_period.value,
            ),
        ]
        if instance.lower_uncertainty_identifier is not None:
            type_ = DatasetType.LOWER_UNCERTAINTY
            possible_values.append(
                ConfigurationParameterPossibleValueRead(
                    configuration_parameter_name="uncertainty_type",
                    configuration_parameter_display_name_english=type_.get_param_display_name(
                        LOCALE_EN
                    ),
                    configuration_parameter_display_name_italian=type_.get_param_display_name(
                        LOCALE_IT
                    ),
                    configuration_parameter_value=type_.value,
                ),
            )
        if instance.upper_uncertainty_identifier is not None:
            type_ = DatasetType.UPPER_UNCERTAINTY
            possible_values.append(
                ConfigurationParameterPossibleValueRead(
                    configuration_parameter_name="uncertainty_type",
                    configuration_parameter_display_name_english=type_.get_param_display_name(
                        LOCALE_EN
                    ),
                    configuration_parameter_display_name_italian=type_.get_param_display_name(
                        LOCALE_IT
                    ),
                    configuration_parameter_value=type_.value,
                ),
            )
        if instance.forecast_time_window is not None:
            possible_values.append(
                ConfigurationParameterPossibleValueRead(
                    configuration_parameter_name="time_window",
                    configuration_parameter_display_name_english=instance.forecast_time_window.display_name_english,
                    configuration_parameter_display_name_italian=instance.forecast_time_window.display_name_italian,
                    configuration_parameter_value=instance.forecast_time_window.name,
                ),
            )
        return possible_values


class LegacyHistoricalCoverageReadDetail(LegacyHistoricalCoverageReadListItem):
    data_precision: int
    decade: Optional[str] = None
    description_english: str
    description_italian: str
    display_name_english: str
    display_name_italian: str
    file_download_url: pydantic.AnyHttpUrl
    identifier: str
    legend: CoverageImageLegend
    name: str
    observation_stations_vector_tile_layer_url: str | None = None
    possible_values: list[ConfigurationParameterPossibleValueRead]
    reference_period: Optional[HistoricalReferencePeriod] = None
    related_coverage_configuration_url: str
    unit_english: str
    unit_italian: str
    url: pydantic.AnyHttpUrl
    wms_base_url: pydantic.AnyHttpUrl
    wms_main_layer_name: str | None = None
    year_period: HistoricalYearPeriod

    @classmethod
    def from_db_instance(
        cls,
        instance: HistoricalCoverageInternal,
        request: Request,
        settings: ArpavPpcvSettings,
        legend_colors: list[tuple[float, str]],
    ) -> "LegacyHistoricalCoverageReadDetail":
        vector_tile_stations_url = None
        if len(instance.configuration.observation_series_configuration_links) > 0:
            vector_tile_stations_url = instance.configuration.observation_series_configuration_links[
                0
            ].observation_series_configuration.get_observation_stations_vector_tile_layer_url(
                settings
            )
        return cls(
            url=str(
                request.url_for(
                    "legacy_get_coverage", coverage_identifier=instance.identifier
                )
            ),
            identifier=instance.identifier,
            name=instance.identifier,
            display_name_english=instance.configuration.climatic_indicator.display_name_english,
            display_name_italian=instance.configuration.climatic_indicator.display_name_italian,
            description_english=instance.configuration.climatic_indicator.description_english,
            description_italian=instance.configuration.climatic_indicator.description_italian,
            related_coverage_configuration_url=str(
                request.url_for(
                    "legacy_get_coverage_configuration",
                    coverage_configuration_identifier=instance.configuration.identifier,
                )
            ),
            wms_base_url=str(
                request.url_for("wms_endpoint", coverage_identifier=instance.identifier)
            ),
            year_period=instance.year_period.value,
            reference_period=(
                instance.configuration.reference_period.value
                if instance.configuration.reference_period
                else None
            ),
            decade=instance.decade.value if instance.decade else None,
            file_download_url=str(
                request.url_for(
                    "get_forecast_data", coverage_identifier=instance.identifier
                )
            ),
            wms_main_layer_name=instance.get_wms_main_layer_name(),
            possible_values=cls.prepare_possible_values(instance),
            observation_stations_vector_tile_layer_url=vector_tile_stations_url,
            unit_english=instance.configuration.climatic_indicator.unit_english,
            unit_italian=instance.configuration.climatic_indicator.unit_italian,
            data_precision=instance.configuration.climatic_indicator.data_precision,
            legend=CoverageImageLegend(
                color_entries=[
                    ImageLegendColor(value=v, color=c) for v, c in legend_colors
                ]
            ),
        )


class LegacyCoverageList(pydantic.BaseModel):
    items: list[
        typing.Union[
            LegacyForecastCoverageReadListItem,
            LegacyHistoricalCoverageReadListItem,
        ]
    ]
    meta: ListMeta
    links: ListLinks
    path_operation_name: typing.ClassVar[str] = "legacy_list_coverage_configurations"

    @classmethod
    def from_items(
        cls,
        forecast_coverages: typing.Sequence[ForecastCoverageInternal],
        historical_coverages: typing.Sequence[HistoricalCoverageInternal],
        request: Request,
        *,
        limit: int,
        offset: int,
        filtered_total_forecast_coverages: int,
        filtered_total_historical_coverages: int,
        unfiltered_total_forecast_coverages: int,
        unfiltered_total_historical_coverages: int,
    ):
        all_items: list[
            typing.Union[
                LegacyForecastCoverageReadListItem,
                LegacyHistoricalCoverageReadListItem,
            ]
        ] = [
            LegacyForecastCoverageReadListItem.from_db_instance(i, request)
            for i in forecast_coverages
        ]
        all_items.extend(
            [
                LegacyHistoricalCoverageReadListItem.from_db_instance(i, request)
                for i in historical_coverages
            ]
        )
        relevant = all_items[offset : offset + limit]
        filtered_total = (
            filtered_total_forecast_coverages + filtered_total_historical_coverages
        )

        return cls(
            meta=get_meta(
                num_returned_records=len(relevant),
                unfiltered_total=(
                    unfiltered_total_forecast_coverages
                    + unfiltered_total_historical_coverages
                ),
                filtered_total=filtered_total,
            ),
            links=get_list_links(
                request,
                cls.path_operation_name,
                limit,
                offset,
                filtered_total,
                len(relevant),
            ),
            items=relevant,
        )


class LegacyForecastCoverageList(WebResourceList):
    items: list[LegacyForecastCoverageReadListItem]
    path_operation_name = "legacy_list_forecast_coverage_identifiers"

    @classmethod
    def from_items(
        cls,
        items: typing.Sequence[ForecastCoverageInternal],
        request: Request,
        *,
        limit: int,
        offset: int,
        filtered_total: int,
        unfiltered_total: int,
    ):
        return cls(
            meta=get_meta(len(items), unfiltered_total, filtered_total),
            links=get_list_links(
                request,
                cls.path_operation_name,
                limit,
                offset,
                filtered_total,
                len(items),
            ),
            items=[
                LegacyForecastCoverageReadListItem.from_db_instance(i, request)
                for i in items
            ],
        )


class LegacyConfigurationParameterList(WebResourceList):
    items: list[ConfigurationParameterReadListItem]
    list_item_type = ConfigurationParameterReadListItem
    path_operation_name = "legacy_list_configuration_parameters"


class CoverageDataDownloadListMeta(pydantic.BaseModel):
    returned_records: int


class ForecastCoverageDownloadList(pydantic.BaseModel):
    meta: CoverageDataDownloadListMeta
    links: ListLinks
    coverage_download_links: list[str]

    @classmethod
    def from_items(
        cls,
        coverages: list[ForecastCoverageInternal],
        request: Request,
        *,
        limit: int,
        offset: int,
        total: int,
    ):
        pagination_urls = get_pagination_urls(
            request.url_for("list_forecast_data_download_links"),
            len(coverages),
            total_records=total,
            limit=limit,
            offset=offset,
        )
        return cls(
            meta=CoverageDataDownloadListMeta(
                returned_records=len(coverages),
                total_records=total,
            ),
            links=ListLinks(**pagination_urls),
            coverage_download_links=[
                f"{request.url_for('get_forecast_data', coverage_identifier=c.identifier)}"
                for c in coverages
            ],
        )


class HistoricalCoverageDownloadList(pydantic.BaseModel):
    meta: CoverageDataDownloadListMeta
    links: ListLinks
    coverage_download_links: list[str]

    @classmethod
    def from_items(
        cls,
        coverages: list[HistoricalCoverageInternal],
        request: Request,
        *,
        limit: int,
        offset: int,
        total: int,
    ):
        pagination_urls = get_pagination_urls(
            request.url_for("list_historical_data_download_links"),
            len(coverages),
            total_records=total,
            limit=limit,
            offset=offset,
        )
        return cls(
            meta=CoverageDataDownloadListMeta(
                returned_records=len(coverages),
                total_records=total,
            ),
            links=ListLinks(**pagination_urls),
            coverage_download_links=[
                f"{request.url_for('get_historical_data', coverage_identifier=c.identifier)}"
                for c in coverages
            ],
        )
