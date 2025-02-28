import logging
import typing

import pydantic
import sqlmodel
from fastapi import Request

from ....schemas import base as base_schemas

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
