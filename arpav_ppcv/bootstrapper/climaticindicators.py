from ..schemas.static import (
    AggregationPeriod,
    MeasureType,
)
from ..schemas.climaticindicators import ClimaticIndicatorCreate

_tas_name = "tas"
_tas_display_name_english = "Average temperature (TAS)"
_tas_display_name_italian = "Temperatura media (TAS)"
_tas_description_english = "Daily mean air temperature close to the ground"
_tas_description_italian = "Temperatura media giornaliera dell'aria vicino al suolo"
_tas_unit_english = "ºC"
_tas_unit_italian = "ºC"


def generate_climatic_indicators() -> list[ClimaticIndicatorCreate]:
    return [
        ClimaticIndicatorCreate(
            name=_tas_name,
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english=_tas_display_name_english,
            display_name_italian=_tas_display_name_italian,
            description_english=_tas_description_english,
            description_italian=_tas_description_italian,
            unit_english=_tas_unit_english,
            unit_italian=_tas_unit_italian,
            palette="default/seq-YlOrRd",
            color_scale_min=-3,
            color_scale_max=32,
            data_precision=1,
            sort_order=0,
        ),
        ClimaticIndicatorCreate(
            name=_tas_name,
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english=_tas_display_name_english,
            display_name_italian=_tas_display_name_italian,
            description_english=_tas_description_english,
            description_italian=_tas_description_italian,
            unit_english=_tas_unit_english,
            unit_italian=_tas_unit_italian,
            palette="default/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=6,
            data_precision=1,
            sort_order=0,
        ),
        ClimaticIndicatorCreate(
            name=_tas_name,
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english=_tas_display_name_english,
            display_name_italian=_tas_display_name_italian,
            description_english=_tas_description_english,
            description_italian=_tas_description_italian,
            unit_english=_tas_unit_english,
            unit_italian=_tas_unit_italian,
            palette="default/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=6,
            data_precision=1,
            sort_order=0,
        ),
    ]
