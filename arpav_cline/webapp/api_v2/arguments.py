"""Central place to define API path operation arguments.

This module defines most API path operation arguments that are reusable by
the various API Path operations. It exists in order to aid enforcing
security-related definitions, like ensuring that input strings are bounded.
"""

from typing import Annotated

from fastapi import (
    Query,
    Path,
)


COVERAGE_IDENTIFIER_QUERY_PARAMETER = Annotated[str, Query(max_length=100)]


COVERAGE_IDENTIFIER_PATH_PARAMETER = Annotated[str, Path(max_length=100)]

FORECAST_COVERAGE_IDENTIFIER_PATH_PARAMETER = Annotated[
    str, Path(pattern=r"^forecast-.*", max_length=100)
]

HISTORICAL_COVERAGE_IDENTIFIER_PATH_PARAMETER = Annotated[
    str, Path(pattern=r"^historical-.*", max_length=100)
]


COVERAGE_CONFIGURATION_IDENTIFIER_PATH_PARAMETER = Annotated[str, Path(max_length=100)]
