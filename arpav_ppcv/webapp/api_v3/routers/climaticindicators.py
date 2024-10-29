import logging
from typing import (
    Annotated,
)

from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from sqlmodel import Session

from .... import (
    database,
)
from ....config import ArpavPpcvSettings
from ... import dependencies
from ..schemas import climaticindicators as read_schemas

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    response_model=read_schemas.ClimaticIndicatorList,
)
def list_climatic_indicators(
    request: Request,
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    list_params: Annotated[dependencies.CommonListFilterParameters, Depends()],
    name_contains: str | None = None,
    measure_type_contains: str | None = None,
    aggregation_period_contains: str | None = None,
):
    """List climatic indicators."""
    climatic_indicators, filtered_total = database.list_climatic_indicators(
        db_session,
        limit=list_params.limit,
        offset=list_params.offset,
        include_total=True,
        name_filter=name_contains,
        measure_type_filter=measure_type_contains,
        aggregation_period_filter=aggregation_period_contains,
    )
    _, unfiltered_total = database.list_climatic_indicators(
        db_session,
        limit=1,
        offset=0,
        include_total=True,
    )
    items = []
    for climatic_indicator in climatic_indicators:
        items.append(
            read_schemas.ClimaticIndicatorReadListItem.from_db_instance(
                climatic_indicator, settings, request
            )
        )
    return read_schemas.ClimaticIndicatorList.from_items(
        items,
        request,
        limit=list_params.limit,
        offset=list_params.offset,
        filtered_total=filtered_total,
        unfiltered_total=unfiltered_total,
    )


@router.get(
    "/{climatic_indicator_identifier}",
    response_model=read_schemas.ClimaticIndicatorReadListItem,
)
def get_climatic_indicator(
    request: Request,
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    climatic_indicator_identifier: str,
):
    db_climatic_indicator = database.get_climatic_indicator_by_identifier(
        db_session, climatic_indicator_identifier
    )
    return read_schemas.ClimaticIndicatorReadListItem.from_db_instance(
        db_climatic_indicator, settings, request
    )
