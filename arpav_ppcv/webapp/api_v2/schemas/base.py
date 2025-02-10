import datetime as dt
import logging
import math
import typing

import pandas as pd
import pydantic
import sqlmodel
from fastapi import Request

from ....config import (
    LOCALE_EN,
    LOCALE_IT,
)
from ....schemas import (
    base as base_schemas,
    observations as observations_schemas,
    coverages as coverages_schemas,
)
from ....schemas.base import (
    StaticObservationSeriesParameter,
    StaticCoverageSeriesParameter,
)

logger = logging.getLogger(__name__)
R = typing.TypeVar("R", bound="ApiReadableModel")


class AppInformation(pydantic.BaseModel):
    version: str
    git_commit: str


@typing.runtime_checkable
class ApiReadableModel(typing.Protocol):
    """Protocol to be used by all schema models that represent API resources.

    It includes the `from_db_instance()` class method, which is to be used for
    constructing instances.
    """

    @classmethod
    def from_db_instance(  # noqa: D102
        cls: typing.Type[R], db_instance: sqlmodel.SQLModel, request: Request
    ) -> R:
        ...


class ListMeta(pydantic.BaseModel):
    returned_records: int
    total_records: int
    total_filtered_records: int


class ListLinks(pydantic.BaseModel):
    self: str
    next: str | None = None
    previous: str | None = None
    first: str | None = None
    last: str | None = None


class TimeSeriesItem(pydantic.BaseModel):
    value: float
    datetime: dt.datetime


class TimeSeriesTranslations(pydantic.BaseModel):
    # series_name: dict[str, str]
    # processing_method: dict[str, str]
    parameter_names: typing.Optional[dict[str, dict[str, str]]] = None
    parameter_values: typing.Optional[dict[str, dict[str, str]]] = None


class TimeSeries(pydantic.BaseModel):
    name: str
    values: list[TimeSeriesItem]
    info: typing.Optional[dict[str, str | int | float | bool | dict]] = None
    translations: typing.Optional[TimeSeriesTranslations] = None

    @classmethod
    def from_observation_series(
        cls,
        series: pd.Series,
        station: observations_schemas.Station,
        variable: observations_schemas.Variable,
        smoothing_strategy: base_schemas.ObservationDataSmoothingStrategy,
        extra_info: typing.Optional[dict[str, str | int | float | dict]] = None,
        derived_series: typing.Optional[base_schemas.ObservationDerivedSeries] = None,
    ):
        if derived_series is not None:
            series_elaboration = base_schemas.TimeSeriesElaboration.DERIVED
            name = "_".join((variable.name, derived_series.value))
            translated_name = {
                LOCALE_EN.language: " - ".join(
                    (
                        variable.display_name_english,
                        derived_series.get_display_name(LOCALE_EN),
                    )
                ),
                LOCALE_IT.language: " - ".join(
                    (
                        variable.display_name_italian,
                        derived_series.get_display_name(LOCALE_IT),
                    )
                ),
            }
        else:
            series_elaboration = base_schemas.TimeSeriesElaboration.ORIGINAL
            name = variable.name
            translated_name = {
                LOCALE_EN.language: variable.display_name_english,
                LOCALE_IT.language: variable.display_name_italian,
            }
        return cls(
            name=name,
            values=[
                TimeSeriesItem(datetime=timestamp, value=value)
                for timestamp, value in series.to_dict().items()
                if not math.isnan(value)
            ],
            info={
                "processing_method": smoothing_strategy.value,
                "station": station.name,
                "variable": variable.name,
                "series_elaboration": series_elaboration.value,
                "derived_series": (
                    derived_series.value if derived_series is not None else ""
                ),
                **(extra_info or {}),
            },
            translations=TimeSeriesTranslations(
                parameter_names={
                    "series_name": {
                        LOCALE_EN.language: (
                            StaticObservationSeriesParameter.SERIES_NAME.get_display_name(
                                LOCALE_EN
                            )
                        ),
                        LOCALE_IT.language: (
                            StaticObservationSeriesParameter.SERIES_NAME.get_display_name(
                                LOCALE_IT
                            )
                        ),
                    },
                    "processing_method": {
                        LOCALE_EN.language: (
                            StaticObservationSeriesParameter.PROCESSING_METHOD.get_display_name(
                                LOCALE_EN
                            )
                        ),
                        LOCALE_IT.language: (
                            StaticObservationSeriesParameter.PROCESSING_METHOD.get_display_name(
                                LOCALE_IT
                            )
                        ),
                    },
                    "station": {
                        LOCALE_EN.language: (
                            StaticObservationSeriesParameter.STATION.get_display_name(
                                LOCALE_EN
                            )
                        ),
                        LOCALE_IT.language: (
                            StaticObservationSeriesParameter.STATION.get_display_name(
                                LOCALE_IT
                            )
                        ),
                    },
                    "variable": {
                        LOCALE_EN.language: (
                            StaticObservationSeriesParameter.VARIABLE.get_display_name(
                                LOCALE_EN
                            )
                        ),
                        LOCALE_IT.language: (
                            StaticObservationSeriesParameter.VARIABLE.get_display_name(
                                LOCALE_IT
                            )
                        ),
                    },
                    "series_elaboration": {
                        LOCALE_EN.language: (
                            StaticObservationSeriesParameter.SERIES_ELABORATION.get_display_name(
                                LOCALE_EN
                            )
                        ),
                        LOCALE_IT.language: (
                            StaticObservationSeriesParameter.SERIES_ELABORATION.get_display_name(
                                LOCALE_IT
                            )
                        ),
                    },
                    "derived_series": {
                        LOCALE_EN.language: (
                            StaticObservationSeriesParameter.DERIVED_SERIES.get_display_name(
                                LOCALE_EN
                            )
                        ),
                        LOCALE_IT.language: (
                            StaticObservationSeriesParameter.DERIVED_SERIES.get_display_name(
                                LOCALE_IT
                            )
                        ),
                    },
                },
                parameter_values={
                    "series_name": translated_name,
                    "processing_method": {
                        LOCALE_EN.language: smoothing_strategy.get_display_name(
                            LOCALE_EN
                        ),
                        LOCALE_IT.language: smoothing_strategy.get_display_name(
                            LOCALE_IT
                        ),
                    },
                    "variable": {
                        LOCALE_EN.language: variable.display_name_english
                        or variable.name,
                        LOCALE_IT.language: variable.display_name_italian
                        or variable.name,
                    },
                    "station": {
                        LOCALE_EN.language: station.name,
                        LOCALE_IT.language: station.name,
                    },
                    "series_elaboration": {
                        LOCALE_EN.language: series_elaboration.get_display_name(
                            LOCALE_EN
                        ),
                        LOCALE_IT.language: series_elaboration.get_display_name(
                            LOCALE_IT
                        ),
                    },
                    "derived_series": {
                        LOCALE_EN.language: derived_series.get_display_name(LOCALE_EN)
                        if derived_series
                        else "",
                        LOCALE_IT.language: derived_series.get_display_name(LOCALE_IT)
                        if derived_series
                        else "",
                    },
                },
            ),
        )

    @classmethod
    def from_coverage_series(
        cls,
        series: pd.Series,
        coverage: coverages_schemas.CoverageInternal,
        smoothing_strategy: base_schemas.CoverageDataSmoothingStrategy,
    ):
        info = {}
        param_names_translations = {}
        param_values_translations = {}
        for pv in coverage.configuration.retrieve_used_values(coverage.identifier):
            conf_param = pv.configuration_parameter_value.configuration_parameter
            info[conf_param.name] = pv.configuration_parameter_value.name
            param_names_translations[conf_param.name] = {
                LOCALE_EN.language: (
                    conf_param.display_name_english or conf_param.name
                ),
                LOCALE_IT.language: (
                    conf_param.display_name_italian or conf_param.name
                ),
            }
            param_values_translations[conf_param.name] = {
                LOCALE_EN.language: (
                    pv.configuration_parameter_value.display_name_english
                    or pv.configuration_parameter_value.name
                ),
                LOCALE_IT.language: (
                    pv.configuration_parameter_value.display_name_italian
                    or pv.configuration_parameter_value.name
                ),
            }
        logger.info(f"serializing {coverage.identifier=} {smoothing_strategy=}...")
        return TimeSeries(
            name=str(series.name),
            values=[
                TimeSeriesItem(datetime=timestamp, value=value)
                for timestamp, value in series.to_dict().items()
                if not math.isnan(value)
            ],
            info={
                "processing_method": smoothing_strategy.value,
                "coverage_identifier": coverage.identifier,
                "coverage_configuration": coverage.configuration.name,
                **info,
            },
            translations=TimeSeriesTranslations(
                parameter_names={
                    "series_name": {
                        LOCALE_EN.language: (
                            StaticCoverageSeriesParameter.SERIES_NAME.get_display_name(
                                LOCALE_EN
                            )
                        ),
                        LOCALE_IT.language: (
                            StaticCoverageSeriesParameter.SERIES_NAME.get_display_name(
                                LOCALE_IT
                            )
                        ),
                    },
                    "processing_method": {
                        LOCALE_EN.language: (
                            StaticCoverageSeriesParameter.PROCESSING_METHOD.get_display_name(
                                LOCALE_EN
                            )
                        ),
                        LOCALE_IT.language: (
                            StaticCoverageSeriesParameter.PROCESSING_METHOD.get_display_name(
                                LOCALE_IT
                            )
                        ),
                    },
                    "coverage_identifier": {
                        LOCALE_EN.language: (
                            StaticCoverageSeriesParameter.COVERAGE_IDENTIFIER.get_display_name(
                                LOCALE_EN
                            )
                        ),
                        LOCALE_IT.language: (
                            StaticCoverageSeriesParameter.COVERAGE_IDENTIFIER.get_display_name(
                                LOCALE_IT
                            )
                        ),
                    },
                    "coverage_configuration": {
                        LOCALE_EN.language: (
                            StaticCoverageSeriesParameter.COVERAGE_CONFIGURATION.get_display_name(
                                LOCALE_EN
                            )
                        ),
                        LOCALE_IT.language: (
                            StaticCoverageSeriesParameter.COVERAGE_CONFIGURATION.get_display_name(
                                LOCALE_IT
                            )
                        ),
                    },
                    **param_names_translations,
                },
                parameter_values={
                    "series_name": {
                        LOCALE_EN.language: (
                            coverage.configuration.display_name_english
                            or coverage.configuration.name
                        ),
                        LOCALE_IT.language: (
                            coverage.configuration.display_name_italian
                            or coverage.configuration.name
                        ),
                    },
                    "processing_method": {
                        LOCALE_EN.language: smoothing_strategy.get_display_name(
                            LOCALE_EN
                        ),
                        LOCALE_IT.language: smoothing_strategy.get_display_name(
                            LOCALE_IT
                        ),
                    },
                    "coverage_identifier": {
                        LOCALE_EN.language: coverage.identifier,
                        LOCALE_IT.language: coverage.identifier,
                    },
                    "coverage_configuration": {
                        LOCALE_EN.language: (
                            coverage.configuration.display_name_english
                            or coverage.configuration.name
                        ),
                        LOCALE_IT.language: (
                            coverage.configuration.display_name_italian
                            or coverage.configuration.name
                        ),
                    },
                    **param_values_translations,
                },
            ),
        )


class TimeSeriesList(pydantic.BaseModel):
    series: list[TimeSeries]


class WebResourceList(base_schemas.ResourceList):
    meta: ListMeta
    links: ListLinks
    list_item_type: typing.ClassVar[typing.Type[ApiReadableModel]]
    path_operation_name: typing.ClassVar[str]

    @classmethod
    def from_items(
        cls,
        items: typing.Sequence[sqlmodel.SQLModel],
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
            items=[cls.list_item_type.from_db_instance(i, request) for i in items],
        )


def get_pagination_urls(
    base_url: str,
    returned_records: int,
    total_records: int,
    limit: int,
    offset: int,
    **filters,
) -> dict[str, str]:
    """Build pagination-related urls."""
    pagination_offsets = _get_pagination_offsets(
        returned_records, total_records, limit, offset
    )
    pagination_urls = {}
    for link_rel, offset in pagination_offsets.items():
        if offset is not None:
            pagination_urls[link_rel] = _build_list_url(
                base_url, limit, offset, **filters
            )
    return pagination_urls


def _build_list_url(base_url: str, limit: int, offset: typing.Optional[int], **filters):
    """Build a URL suitable for a list page."""
    url = f"{base_url}?limit={limit}"
    remaining = {"offset": offset, **filters}
    for filter_name, filter_value in remaining.items():
        if filter_value is not None:
            url = "&".join((url, f"{filter_name}={filter_value}"))
    return url


def _get_pagination_offsets(
    returned_records: int, total_records: int, limit: int, offset: int
):
    """Calculate pagination offsets."""
    shown = offset + returned_records
    has_next = total_records > shown
    has_previous = shown > returned_records
    return {
        "self": offset,
        "next": offset + limit if has_next else None,
        "previous": offset - limit if has_previous else None,
        "first": 0,
        "last": (total_records // limit) * limit,
    }


def get_list_links(
    request: Request,
    path_operation_name: str,
    limit: int,
    offset: int,
    filtered_total: int,
    num_returned_records: int,
) -> ListLinks:
    filters = dict(request.query_params)
    if "limit" in filters.keys():
        del filters["limit"]
    if "offset" in filters.keys():
        del filters["offset"]
    pagination_urls = get_pagination_urls(
        request.url_for(path_operation_name),
        num_returned_records,
        filtered_total,
        limit,
        offset,
        **filters,
    )
    return ListLinks(**pagination_urls)


def get_meta(
    num_returned_records: int, unfiltered_total: int, filtered_total: int
) -> ListMeta:
    return ListMeta(
        returned_records=num_returned_records,
        total_records=unfiltered_total,
        total_filtered_records=filtered_total,
    )
