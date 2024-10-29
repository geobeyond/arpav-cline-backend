import logging
import pydantic
from fastapi import Request

from .... import palette
from ....config import ArpavPpcvSettings
from ....schemas import (
    climaticindicators as app_models,
    static,
)
from . import base

logger = logging.getLogger(__name__)


class ClimaticIndicatorReadListItem(pydantic.BaseModel):
    url: pydantic.AnyHttpUrl
    identifier: str
    name: str
    measure_type: static.MeasureType
    aggregation_period: static.AggregationPeriod
    display_name_english: str
    display_name_italian: str
    description_english: str
    description_italian: str
    unit_english: str
    unit_italian: str
    data_precision: int
    sort_order: int
    legend: base.CoverageImageLegend

    @classmethod
    def from_db_instance(
        cls,
        instance: app_models.ClimaticIndicator,
        settings: ArpavPpcvSettings,
        request: Request,
    ):
        palette_colors = palette.parse_palette(instance.palette, settings.palettes_dir)
        applied_colors = []
        if palette_colors is not None:
            minimum = instance.color_scale_min
            maximum = instance.color_scale_max
            if abs(maximum - minimum) > 0.001:
                applied_colors = palette.apply_palette(
                    palette_colors,
                    minimum,
                    maximum,
                    num_stops=settings.palette_num_stops,
                )
            else:
                logger.warning(
                    f"Cannot calculate applied colors for coverage "
                    f"configuration {instance.name!r} - check the "
                    f"colorscale min and max values"
                )
        else:
            logger.warning(f"Unable to parse palette {instance.palette!r}")
        return cls(
            **instance.model_dump(),
            url=str(
                request.url_for(
                    "get_climatic_indicator",
                    climatic_indicator_identifier=instance.identifier,
                )
            ),
            legend=base.CoverageImageLegend(
                color_entries=[
                    base.ImageLegendColor(value=v, color=c) for v, c in applied_colors
                ]
            ),
        )


class ClimaticIndicatorList(base.WebResourceList):
    items: list[ClimaticIndicatorReadListItem]
    list_item_type = ClimaticIndicatorReadListItem
    path_operation_name = "list_climatic_indicators"
