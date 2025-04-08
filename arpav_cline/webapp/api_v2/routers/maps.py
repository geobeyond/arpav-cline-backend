import logging
from typing import (
    Annotated,
    Literal,
)

import httpx
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import StreamingResponse
from playwright.sync_api import Error as PlaywrightError
from sqlmodel import Session

from ....config import ArpavPpcvSettings
from .... import (
    db,
    mapdownloads,
)
from ....schemas.static import (
    DataCategory,
)
from ... import dependencies
from ..arguments import (
    COVERAGE_IDENTIFIER_QUERY_PARAMETER,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/map-screenshot",
)
def get_map(
    url: Annotated[str, Query(max_length=500)],
    delay_seconds: Annotated[int, Query(ge=1, le=60)] = 10,
):
    """Get a screenshot representing a map."""
    try:
        screenshot_buffer = mapdownloads.grab_frontend_screenshot(
            url, frontend_settle_delay_seconds=delay_seconds
        )
    except PlaywrightError as err:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(err))
    else:
        return StreamingResponse(
            screenshot_buffer,
            media_type="image/png",
        )


@router.get("/map-print")
def print_map(
    session: Annotated[Session, Depends(dependencies.get_db_session)],
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    http_client: Annotated[httpx.Client, Depends(dependencies.get_sync_http_client)],
    coverage_identifier: COVERAGE_IDENTIFIER_QUERY_PARAMETER,
    main_layer: str | None = None,
    output_format: Annotated[
        Literal["jpg", "png", "pdf"],
        Query(description=("Output format for the printed map.")),
    ] = "png",
    language_code: Literal["en", "it"] = "en",
):
    invalid_cov_identifier_error = "Invalid coverage identifier"
    try:
        data_category = DataCategory(coverage_identifier.partition("-")[0])
        cov_retriever = {
            DataCategory.FORECAST: db.get_forecast_coverage,
            DataCategory.HISTORICAL: db.get_historical_coverage,
        }[data_category]
    except ValueError:
        raise HTTPException(400, detail=invalid_cov_identifier_error)
    if (coverage := cov_retriever(session, coverage_identifier)) is not None:
        existing_main_layer_name = coverage.get_wms_main_layer_name()
        possible_values = [existing_main_layer_name]
        try:
            existing_secondary_layer_name = coverage.get_wms_secondary_layer_name()
        except AttributeError:
            pass  # historical coverages don't have a secondary wms layer name
        else:
            if existing_secondary_layer_name is not None:
                possible_values.append(existing_secondary_layer_name)
        main_layer_name = (
            main_layer if main_layer is not None else existing_main_layer_name
        )
        if main_layer_name in possible_values:
            printed_map_iterator = mapdownloads.get_map_print(
                http_client,
                coverage_identifier,
                output_format,
                settings,
                main_layer=main_layer or coverage.get_wms_main_layer_name(),
                language_code=language_code,
            )
            printed_map_response_headers = next(printed_map_iterator)
            content_type = printed_map_response_headers.get("content-type")
            return StreamingResponse(
                printed_map_iterator,
                media_type=content_type,
                headers={"content-disposition": 'inline; filename="cline-map"'},
            )
        else:
            raise HTTPException(400, detail="Invalid main layer name")
    else:
        raise HTTPException(400, detail=invalid_cov_identifier_error)
