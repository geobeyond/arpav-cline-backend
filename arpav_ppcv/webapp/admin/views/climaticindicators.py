import functools
import logging
from typing import (
    Any,
    Optional,
    Sequence,
    Union,
)

import anyio.to_thread
import starlette_admin
from starlette.requests import Request
from starlette_admin.contrib.sqlmodel import ModelView

from .... import database
from ....schemas.static import (
    AggregationPeriod,
    MeasureType,
)
from ....schemas.climaticindicators import (
    ClimaticIndicatorCreate,
    ClimaticIndicatorUpdate,
)
from .. import schemas as read_schemas

logger = logging.getLogger(__name__)


class ClimaticIndicatorView(ModelView):
    identity = "climatic_indicators"
    name = "Climatic Indicator"
    label = "Climatic Indicators"
    pk_attr = "id"

    exclude_fields_from_list = (
        "id",
        "display_name_english",
        "display_name_italian",
        "description_english",
        "description_italian",
        "unit_english",
        "unit_italian",
        "palette",
        "color_scale_min",
        "color_scale_max",
        "data_precision",
    )
    exclude_fields_from_detail = ("id",)

    fields = (
        starlette_admin.IntegerField("id"),
        starlette_admin.StringField("identifier", read_only=True),
        starlette_admin.StringField("name", required=True),
        starlette_admin.EnumField("measure_type", enum=MeasureType, required=True),
        starlette_admin.EnumField(
            "aggregation_period", enum=AggregationPeriod, required=True
        ),
        starlette_admin.StringField("display_name_english", required=True),
        starlette_admin.StringField("display_name_italian", required=True),
        starlette_admin.StringField("description_english", required=True),
        starlette_admin.StringField("description_italian", required=True),
        starlette_admin.StringField("unit_english", required=True),
        starlette_admin.StringField("unit_italian", required=True),
        starlette_admin.StringField(
            "palette",
            required=True,
            help_text=(
                "Name of the palette that should used by the THREDDS WMS server. "
                "Available values can be found at https://reading-escience-centre.gitbooks.io/ncwms-user-guide/content/04-usage.html#getmap"
            ),
        ),
        starlette_admin.FloatField("color_scale_min", required=True),
        starlette_admin.FloatField("color_scale_max", required=True),
        starlette_admin.IntegerField(
            "data_precision",
            required=True,
            help_text=(
                "Number of decimal places to be used when displaying data values"
            ),
        ),
        starlette_admin.StringField("sort_order"),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon = "fa-solid fa-cloud-sun-rain"

    async def create(self, request: Request, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data)
            await self.validate(request, data)
            climatic_indicator_create = ClimaticIndicatorCreate(
                name=data["name"],
                measure_type=data["measure_type"],
                aggregation_period=data["aggregation_period"],
                display_name_english=data["display_name_english"],
                display_name_italian=data["display_name_italian"],
                description_english=data["description_english"],
                description_italian=data["description_italian"],
                unit_english=data["unit_english"],
                unit_italian=data["unit_italian"],
                palette=data["palette"],
                color_scale_min=data["color_scale_min"],
                color_scale_max=data["color_scale_max"],
                data_precision=data["data_precision"],
                sort_order=data.get("sort_order"),
            )
            db_climatic_indicator = await anyio.to_thread.run_sync(
                database.create_climatic_indicator,
                request.state.session,
                climatic_indicator_create,
            )
            climatic_indicator = read_schemas.ClimaticIndicatorRead(
                **db_climatic_indicator.model_dump(),
            )
            return climatic_indicator
        except Exception as e:
            return self.handle_exception(e)

    async def edit(self, request: Request, pk: Any, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data, True)
            await self.validate(request, data)
            climatic_indicator_update = ClimaticIndicatorUpdate(
                name=data["name"],
                measure_type=data["measure_type"],
                aggregation_period=data["aggregation_period"],
                display_name_english=data["display_name_english"],
                display_name_italian=data["display_name_italian"],
                description_english=data["description_english"],
                description_italian=data["description_italian"],
                unit_english=data["unit_english"],
                unit_italian=data["unit_italian"],
                palette=data["palette"],
                color_scale_min=data["color_scale_min"],
                color_scale_max=data["color_scale_max"],
                data_precision=data["data_precision"],
                sort_order=data.get("sort_order"),
            )
            db_climatic_indicator = await anyio.to_thread.run_sync(
                database.get_climatic_indicator, request.state.session, pk
            )
            db_climatic_indicator = await anyio.to_thread.run_sync(
                database.update_climatic_indicator,
                request.state.session,
                db_climatic_indicator,
                climatic_indicator_update,
            )
            climatic_indicator = read_schemas.ClimaticIndicatorRead(
                **db_climatic_indicator.model_dump(),
            )
            return climatic_indicator
        except Exception as e:
            self.handle_exception(e)

    async def find_by_pk(
        self, request: Request, pk: Any
    ) -> read_schemas.ClimaticIndicatorRead:
        db_climatic_indicator = await anyio.to_thread.run_sync(
            database.get_climatic_indicator, request.state.session, pk
        )
        return read_schemas.ClimaticIndicatorRead(**db_climatic_indicator.model_dump())

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[read_schemas.ClimaticIndicatorRead]:
        list_params = functools.partial(
            database.list_climatic_indicators,
            limit=limit,
            offset=skip,
            name_filter=str(where) if where not in (None, "") else None,
            include_total=False,
        )
        db_climatic_indicators, _ = await anyio.to_thread.run_sync(
            list_params, request.state.session
        )
        return [
            read_schemas.ClimaticIndicatorRead(**ind.model_dump())
            for ind in db_climatic_indicators
        ]
