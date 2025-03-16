import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Query,
)
from fastapi.responses import StreamingResponse

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
    screenshot_buffer = mapdownloads.grab_frontend_screenshot(
        url, delay_seconds=delay_seconds
    )
    return StreamingResponse(
        screenshot_buffer,
        media_type="image/png",
    )
