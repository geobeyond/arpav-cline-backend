import importlib.metadata
import logging
import os

from fastapi import APIRouter

from ..schemas.base import AppInformation


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=AppInformation)
async def get_app_info():
    """Return information about the ARPAV-PPCV application."""
    return {
        "version": importlib.metadata.version("arpav_ppcv_backend"),
        "git_commit": os.getenv("GIT_COMMIT", "unknown"),
    }
