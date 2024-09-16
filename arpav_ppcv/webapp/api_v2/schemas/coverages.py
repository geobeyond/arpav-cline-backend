import uuid
import typing

import pydantic
from fastapi import Request

from ....config import (
    LOCALE_EN,
    LOCALE_IT,
)
from ....schemas import coverages as app_models
from .base import WebResourceList


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
        instance: app_models.ConfigurationParameter,
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
                        }
                    ),
                    display_name_english=pv.display_name_english or pv.name,
                    display_name_italian=pv.display_name_italian or pv.name,
                )
                for pv in instance.allowed_values
            ],
        )


class ConfigurationParameterPossibleValueRead(pydantic.BaseModel):
    configuration_parameter_name: str
    configuration_parameter_display_name_english: str
    configuration_parameter_display_name_italian: str
    configuration_parameter_value: str


class CoverageConfigurationReadListItem(pydantic.BaseModel):
    url: pydantic.AnyHttpUrl
    id: uuid.UUID
    name: str
    display_name_english: str
    display_name_italian: str
    wms_main_layer_name: str | None
    wms_secondary_layer_name: str | None
    coverage_id_pattern: str
    possible_values: list[ConfigurationParameterPossibleValueRead]

    @classmethod
    def from_db_instance(
        cls,
        instance: app_models.CoverageConfiguration,
        request: Request,
    ) -> "CoverageConfigurationReadListItem":
        url = request.url_for(
            "get_coverage_configuration", **{"coverage_configuration_id": instance.id}
        )
        return cls(
            **instance.model_dump(
                exclude={
                    "display_name_english",
                    "display_name_italian",
                }
            ),
            display_name_english=instance.display_name_english or instance.name,
            display_name_italian=instance.display_name_italian or instance.name,
            url=str(url),
            possible_values=[
                ConfigurationParameterPossibleValueRead(
                    configuration_parameter_name=pv.configuration_parameter_value.configuration_parameter.name,
                    configuration_parameter_display_name_english=(
                        pv.configuration_parameter_value.configuration_parameter.display_name_english
                        or pv.configuration_parameter_value.configuration_parameter.name
                    ),
                    configuration_parameter_display_name_italian=(
                        pv.configuration_parameter_value.configuration_parameter.display_name_italian
                        or pv.configuration_parameter_value.configuration_parameter.name
                    ),
                    configuration_parameter_value=pv.configuration_parameter_value.name,
                )
                for pv in instance.possible_values
            ],
        )


class CoverageConfigurationReadDetail(CoverageConfigurationReadListItem):
    url: pydantic.AnyHttpUrl
    unit_english: str
    unit_italian: str
    allowed_coverage_identifiers: list[str]
    description_english: str | None
    description_italian: str | None
    legend: CoverageImageLegend

    @classmethod
    def from_db_instance(
        cls,
        instance: app_models.CoverageConfiguration,
        allowed_coverage_identifiers: list[str],
        legend_colors: list[tuple[float, str]],
        request: Request,
    ) -> "CoverageConfigurationReadDetail":
        url = request.url_for(
            "get_coverage_configuration", **{"coverage_configuration_id": instance.id}
        )
        return cls(
            **instance.model_dump(),
            url=str(url),
            possible_values=[
                ConfigurationParameterPossibleValueRead(
                    configuration_parameter_name=pv.configuration_parameter_value.configuration_parameter.name,
                    configuration_parameter_display_name_english=(
                        pv.configuration_parameter_value.configuration_parameter.display_name_english
                        or pv.configuration_parameter_value.configuration_parameter.name
                    ),
                    configuration_parameter_display_name_italian=(
                        pv.configuration_parameter_value.configuration_parameter.display_name_italian
                        or pv.configuration_parameter_value.configuration_parameter.name
                    ),
                    configuration_parameter_value=pv.configuration_parameter_value.name,
                )
                for pv in instance.possible_values
            ],
            allowed_coverage_identifiers=allowed_coverage_identifiers,
            legend=CoverageImageLegend(
                color_entries=[
                    ImageLegendColor(value=v, color=c) for v, c in legend_colors
                ]
            ),
        )


class CoverageConfigurationList(WebResourceList):
    items: list[CoverageConfigurationReadListItem]
    list_item_type = CoverageConfigurationReadListItem
    path_operation_name = "list_coverage_configurations"


class CoverageIdentifierReadListItem(pydantic.BaseModel):
    identifier: str
    related_coverage_configuration_url: str
    wms_base_url: str
    wms_main_layer_name: str | None = None
    wms_secondary_layer_name: str | None = None
    possible_values: list[ConfigurationParameterPossibleValueRead]

    @classmethod
    def from_db_instance(
        cls,
        instance: app_models.CoverageInternal,
        request: Request,
    ) -> "CoverageIdentifierReadListItem":
        wms_base_url = request.url_for(
            "wms_endpoint", coverage_identifier=instance.identifier
        )
        return cls(
            identifier=instance.identifier,
            wms_base_url=str(wms_base_url),
            wms_main_layer_name=(
                instance.configuration.get_wms_main_layer_name(instance.identifier)
                if instance.configuration.wms_main_layer_name is not None
                else None
            ),
            wms_secondary_layer_name=(
                instance.configuration.get_wms_secondary_layer_name(instance.identifier)
                if instance.configuration.wms_secondary_layer_name is not None
                else None
            ),
            related_coverage_configuration_url=str(
                request.url_for(
                    "get_coverage_configuration",
                    coverage_configuration_id=instance.configuration.id,
                )
            ),
            possible_values=[
                ConfigurationParameterPossibleValueRead(
                    configuration_parameter_name=pv.configuration_parameter_value.configuration_parameter.name,
                    configuration_parameter_display_name_english=(
                        pv.configuration_parameter_value.configuration_parameter.display_name_english
                        or pv.configuration_parameter_value.configuration_parameter.name
                    ),
                    configuration_parameter_display_name_italian=(
                        pv.configuration_parameter_value.configuration_parameter.display_name_italian
                        or pv.configuration_parameter_value.configuration_parameter.name
                    ),
                    configuration_parameter_value=pv.configuration_parameter_value.name,
                )
                for pv in instance.configuration.retrieve_used_values(
                    instance.identifier
                )
            ],
        )


class CoverageIdentifierList(WebResourceList):
    items: list[CoverageIdentifierReadListItem]
    path_operation_name = "list_coverage_identifiers"

    @classmethod
    def from_items(
        cls,
        items: typing.Sequence[app_models.CoverageInternal],
        request: Request,
        *,
        limit: int,
        offset: int,
        filtered_total: int,
        unfiltered_total: int,
    ):
        return cls(
            meta=cls._get_meta(len(items), unfiltered_total, filtered_total),
            links=cls._get_list_links(
                request, limit, offset, filtered_total, len(items)
            ),
            items=[
                CoverageIdentifierReadListItem.from_db_instance(i, request)
                for i in items
            ],
        )


class ConfigurationParameterList(WebResourceList):
    items: list[ConfigurationParameterReadListItem]
    list_item_type = ConfigurationParameterReadListItem
    path_operation_name = "list_configuration_parameters"


class ConfigurationParameterMenuTranslation(pydantic.BaseModel):
    name: dict[str, str]
    description: dict[str, str]


class ForecastMenuTranslations(pydantic.BaseModel):
    variable: dict[str, ConfigurationParameterMenuTranslation]
    aggregation_period: dict[str, ConfigurationParameterMenuTranslation]
    measure: dict[str, ConfigurationParameterMenuTranslation]
    other_parameters: dict[str, dict[str, ConfigurationParameterMenuTranslation]]

    @classmethod
    def from_items(
        cls, variable_menu_trees: typing.Sequence[app_models.ForecastVariableMenuTree]
    ):
        result = {}
        for variable_menu_tree in variable_menu_trees:
            variable_cp = variable_menu_tree["climatological_variable"]
            aggregation_period_cp = variable_menu_tree["aggregation_period"]
            measure_cp = variable_menu_tree["measure"]
            vars = result.setdefault("variable", {})
            vars[variable_cp.name] = ConfigurationParameterMenuTranslation(
                name={
                    LOCALE_EN.language: variable_cp.display_name_english,
                    LOCALE_IT.language: variable_cp.display_name_english,
                },
                description={
                    LOCALE_EN.language: variable_cp.description_english,
                    LOCALE_IT.language: variable_cp.description_italian,
                },
            )
            aggreg_periods = result.setdefault("aggregation_period", {})
            aggreg_periods[
                aggregation_period_cp.name
            ] = ConfigurationParameterMenuTranslation(
                name={
                    LOCALE_EN.language: aggregation_period_cp.display_name_english,
                    LOCALE_IT.language: aggregation_period_cp.display_name_english,
                },
                description={
                    LOCALE_EN.language: aggregation_period_cp.description_english,
                    LOCALE_IT.language: aggregation_period_cp.description_italian,
                },
            )
            measures = result.setdefault("measure", {})
            measures[measure_cp.name] = ConfigurationParameterMenuTranslation(
                name={
                    LOCALE_EN.language: measure_cp.display_name_english,
                    LOCALE_IT.language: measure_cp.display_name_english,
                },
                description={
                    LOCALE_EN.language: measure_cp.description_english,
                    LOCALE_IT.language: measure_cp.description_italian,
                },
            )
            others = result.setdefault("other_parameters", {})
            for combination_info in variable_menu_tree["combinations"].values():
                cp = combination_info["configuration_parameter"]
                param_ = others.setdefault(cp.name, {})
                for cpv in cp.allowed_values:
                    param_[cpv.name] = ConfigurationParameterMenuTranslation(
                        name={
                            LOCALE_EN.language: cpv.display_name_english,
                            LOCALE_IT.language: cpv.display_name_english,
                        },
                        description={
                            LOCALE_EN.language: cpv.description_english,
                            LOCALE_IT.language: cpv.description_italian,
                        },
                    )
        return cls(
            variable=result["variable"],
            aggregation_period=result["aggregation_period"],
            measure=result["measure"],
            other_parameters=result["other_parameters"],
        )


class HistoricalMenuTranslations(pydantic.BaseModel):
    variable: dict[str, ConfigurationParameterMenuTranslation]
    aggregation_period: dict[str, ConfigurationParameterMenuTranslation]
    other_parameters: dict[str, dict[str, ConfigurationParameterMenuTranslation]]

    @classmethod
    def from_items(
        cls, variable_menu_trees: typing.Sequence[app_models.HistoricalVariableMenuTree]
    ):
        result = {}
        for variable_menu_tree in variable_menu_trees:
            variable_cp = variable_menu_tree["historical_variable"]
            aggregation_period_cp = variable_menu_tree["aggregation_period"]
            vars = result.setdefault("variable", {})
            vars[variable_cp.name] = ConfigurationParameterMenuTranslation(
                name={
                    LOCALE_EN.language: variable_cp.display_name_english,
                    LOCALE_IT.language: variable_cp.display_name_english,
                },
                description={
                    LOCALE_EN.language: variable_cp.description_english,
                    LOCALE_IT.language: variable_cp.description_italian,
                },
            )
            aggreg_periods = result.setdefault("aggregation_period", {})
            aggreg_periods[
                aggregation_period_cp.name
            ] = ConfigurationParameterMenuTranslation(
                name={
                    LOCALE_EN.language: aggregation_period_cp.display_name_english,
                    LOCALE_IT.language: aggregation_period_cp.display_name_english,
                },
                description={
                    LOCALE_EN.language: aggregation_period_cp.description_english,
                    LOCALE_IT.language: aggregation_period_cp.description_italian,
                },
            )
            others = result.setdefault("other_parameters", {})
            for combination_info in variable_menu_tree["combinations"].values():
                cp = combination_info["configuration_parameter"]
                param_ = others.setdefault(cp.name, {})
                for cpv in cp.allowed_values:
                    param_[cpv.name] = ConfigurationParameterMenuTranslation(
                        name={
                            LOCALE_EN.language: cpv.display_name_english,
                            LOCALE_IT.language: cpv.display_name_english,
                        },
                        description={
                            LOCALE_EN.language: cpv.description_english,
                            LOCALE_IT.language: cpv.description_italian,
                        },
                    )
        return cls(
            variable=result["variable"],
            aggregation_period=result["aggregation_period"],
            other_parameters=result["other_parameters"],
        )


class ForecastVariableCombinations(pydantic.BaseModel):
    variable: str
    aggregation_period: str
    measure: str
    other_parameters: dict[str, list[str]]

    @classmethod
    def from_items(cls, menu_tree: app_models.ForecastVariableMenuTree):
        combinations = {}
        for param_name, param_combinations in menu_tree["combinations"].items():
            combinations[param_name] = []
            for valid_value in param_combinations["values"]:
                combinations[param_name].append(valid_value.name)

        return cls(
            variable=menu_tree["climatological_variable"].name,
            aggregation_period=menu_tree["aggregation_period"].name,
            measure=menu_tree["measure"].name,
            other_parameters=combinations,
        )


class HistoricalVariableCombinations(pydantic.BaseModel):
    variable: str
    aggregation_period: str
    other_parameters: dict[str, list[str]]

    @classmethod
    def from_items(cls, menu_tree: app_models.HistoricalVariableMenuTree):
        combinations = {}
        for param_name, param_combinations in menu_tree["combinations"].items():
            combinations[param_name] = []
            for valid_value in param_combinations["values"]:
                combinations[param_name].append(valid_value.name)

        return cls(
            variable=menu_tree["historical_variable"].name,
            aggregation_period=menu_tree["aggregation_period"].name,
            other_parameters=combinations,
        )


class ForecastVariableCombinationsList(pydantic.BaseModel):
    combinations: list[ForecastVariableCombinations]
    translations: ForecastMenuTranslations


class HistoricalVariableCombinationsList(pydantic.BaseModel):
    combinations: list[HistoricalVariableCombinations]
    translations: HistoricalMenuTranslations
