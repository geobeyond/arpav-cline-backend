from ...schemas.static import (
    AggregationPeriod,
    MeasureType,
)
from ...schemas.climaticindicators import ClimaticIndicatorCreate


def generate_climatic_indicators() -> list[ClimaticIndicatorCreate]:
    return [
        ClimaticIndicatorCreate(
            name="tasmin",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Minimum temperature (TASMIN)",
            display_name_italian="Temperatura minima (TASMIN)",
            description_english=("Daily minimum air temperature close to the ground"),
            description_italian=(
                "Temperatura minima giornaliera dell'aria vicino al suolo"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/seq-YlOrRd",
            color_scale_min=-3,
            color_scale_max=32,
            data_precision=1,
            sort_order=1,
        ),
        ClimaticIndicatorCreate(
            name="tasmin",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Minimum temperature (TASMIN)",
            display_name_italian="Temperatura minima (TASMIN)",
            description_english=("Daily minimum air temperature close to the ground"),
            description_italian=(
                "Temperatura minima giornaliera dell'aria vicino al suolo"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/seq-YlOrRd",
            color_scale_min=-5,
            color_scale_max=32,
            data_precision=1,
            sort_order=1,
        ),
        ClimaticIndicatorCreate(
            name="tasmin",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Minimum temperature (TASMIN)",
            display_name_italian="Temperatura minima (TASMIN)",
            description_english=("Daily minimum air temperature close to the ground"),
            description_italian=(
                "Temperatura minima giornaliera dell'aria vicino al suolo"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="uncert-stippled/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=6,
            data_precision=1,
            sort_order=1,
        ),
    ]
