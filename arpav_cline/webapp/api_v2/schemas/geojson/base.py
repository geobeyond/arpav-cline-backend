import typing

import geojson_pydantic
import pydantic
from fastapi.requests import Request

from ..base import (
    ListLinks,
    get_pagination_urls,
)

F = typing.TypeVar("F", bound="ApiReadableModelAsFeature")


@typing.runtime_checkable
class ApiReadableModelAsFeature(typing.Protocol):
    """Protocol to be used by all schema models that represent API resources.

    It includes the `from_db_instance()` class method, which is to be used for
    constructing instances.
    """

    @classmethod
    def from_db_instance(  # noqa: D102
        cls: typing.Type[F], db_instance: pydantic.BaseModel, request: Request
    ) -> F:
        ...


class ArpavFeatureCollection(geojson_pydantic.FeatureCollection):
    list_item_type: typing.ClassVar[typing.Type[ApiReadableModelAsFeature]]
    path_operation_name: typing.ClassVar[str]

    type: str = "FeatureCollection"
    links: ListLinks
    number_matched: int
    number_total: int
    number_returned: int

    @classmethod
    def from_items(
        cls,
        items: typing.Sequence[pydantic.BaseModel],
        request: Request,
        *,
        limit: int,
        offset: int,
        filtered_total: int,
        unfiltered_total: int,
    ) -> "ArpavFeatureCollection":
        return cls(
            features=[cls.list_item_type.from_db_instance(i, request) for i in items],
            links=cls._get_list_links(
                request, limit, offset, filtered_total, len(items)
            ),
            number_matched=filtered_total,
            number_total=unfiltered_total,
            number_returned=len(items),
        )

    @classmethod
    def _get_list_links(
        cls,
        request: Request,
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
            request.url_for(cls.path_operation_name),
            num_returned_records,
            filtered_total,
            limit,
            offset,
            **filters,
        )
        return ListLinks(**pagination_urls)
