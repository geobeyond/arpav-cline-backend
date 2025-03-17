import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import StreamingResponse
from playwright.sync_api import Error as PlaywrightError

from .... import mapdownloads

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/map-screenshot",
)
def get_map(
    url: Annotated[str, Query(max_length=255)],
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
