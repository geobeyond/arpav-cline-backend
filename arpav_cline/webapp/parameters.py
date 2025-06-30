"""Centralized location for API parameters.

This allows easier enforcing of parameter bounds checks, etc.
"""

from typing import Annotated

from fastapi import (
    Path,
    Query,
)
from fastapi.openapi.models import Example

COVERAGE_IDENTIFIER_PATH_PARAMETER = Annotated[
    str,
    Path(
        max_length=500,
        description="Identifier of the coverage to retrieve",
    ),
]

COORDS_POINT_QUERY_PARAMETER = Annotated[
    str,
    Query(
        max_length=50,
        description=(
            "Coordinates of the point to retrieve, expressed in "
            "[Well-Known Text notation](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry)"
        ),
    ),
]

DEFAULT_COORDS_POINT_QUERY_PARAMETER = "POINT(12.314 45.407)"

MANN_KENDALL_DATETIME_QUERY_PARAMETER = Annotated[
    str | None,
    Query(
        max_length=50,
        description=(
            "Optional start and end year for Mann-Kendall test.<br><br>"
            "The expected format for this parameter is described in the "
            "[OGC API - EDR standard](https://docs.ogc.org/is/19-086r6/19-086r6.html#req_core_rc-time-response).<br><br>"
            "In short, if provided, this must be a string of the form `{start}/{end}` "
            "where `{start}` and `{end}` can "
            "be either an ISO8601 date or the special string `..` to indicate that "
            "the respective dataset's `start` or `end` should be used. Partial "
            "ISO8601 dates are allowed (_e.g._ specifying just the year, as in `2020`, "
            "or just the year and month, as in `2020-01`). Also note that, if "
            "provided, the year span between `{start}` and `{end}` must be at least "
            "27 years"
        ),
        examples=["1991/2018", "../2030", "1990/..", "../.."],
        openapi_examples={
            "start_and_end": Example(
                summary="Provide both a start and end date",
                description=(
                    "If both start and end are provided, the year span between them "
                    "must be at least 27 years"
                ),
                value="1991/2018",
            ),
            "omit_start": Example(
                summary="Omit start date",
                description=(
                    "If the start date is replaced with the special '..' string, the "
                    "start date used will the same as the underlying data's."
                ),
                value=".../2018",
            ),
            "omit_end": Example(
                summary="Omit end date",
                description=(
                    "If the end date is replaced with the special '..' string, the "
                    "end date used will the same as the underlying data's."
                ),
                value="2018/...",
            ),
            "omit_both": Example(
                summary="Omit both start and end dates",
                description=(
                    "If both the start and end dates are replaced with the special "
                    "'..' string, then the underlying dataset's temporal bounds will "
                    "be used. This is equivalent to omitting this parameter altogether."
                ),
                value="../...",
            ),
        },
    ),
]

TIME_SERIES_DATETIME_QUERY_PARAMETER = Annotated[
    str | None,
    Query(
        max_length=50,
        description=(
            "Optional start and end year for the time series.<br><br>"
            "The expected format for this parameter is described in the "
            "[OGC API - EDR standard](https://docs.ogc.org/is/19-086r6/19-086r6.html#req_core_rc-time-response).<br><br>"
            "In short, if provided, this must be a string of the form `{start}/{end}` "
            "where `{start}` and `{end}` can be either an ISO8601 date or the special "
            "string `..` to indicate that the respective dataset's `start` or `end` "
            "should be used. Partial ISO8601 dates are allowed (_e.g._ specifying "
            "just the year, as in `2020`, or just the year and month, as in "
            "`2020-01`)."
        ),
        examples=["1991/2018", "../2030", "1990/..", "../.."],
        openapi_examples={
            "start_and_end": Example(
                summary="Provide both a start and end date",
                description=(
                    "If both start and end are provided, they are used as the time "
                    "series year span"
                ),
                value="1991/2018",
            ),
            "omit_start": Example(
                summary="Omit start date",
                description=(
                    "If the start date is replaced with the special '..' string, the "
                    "start date used will the same as the underlying data's."
                ),
                value=".../2018",
            ),
            "omit_end": Example(
                summary="Omit end date",
                description=(
                    "If the end date is replaced with the special '..' string, the "
                    "end date used will the same as the underlying data's."
                ),
                value="2018/...",
            ),
            "omit_both": Example(
                summary="Omit both start and end dates",
                description=(
                    "If both the start and end dates are replaced with the special "
                    "'..' string, then the underlying dataset's temporal bounds will "
                    "be used. This is equivalent to omitting this parameter altogether."
                ),
                value="../...",
            ),
        },
    ),
]
