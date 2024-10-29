from ...schemas.static import (
    AggregationPeriod,
    MeasureType,
)
from ...schemas.climaticindicators import ClimaticIndicatorCreate


def generate_climatic_indicators() -> list[ClimaticIndicatorCreate]:
    return [
        ClimaticIndicatorCreate(
            name="su30",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Summer days (SU30)",
            display_name_italian="Giorni caldi (SU30)",
            description_english=(
                "Number of days with maximum temperature larger than 30°C"
            ),
            description_italian=(
                "Numero di giorni con temperatura massima maggiore di 30°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="default/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=100,
            data_precision=0,
            sort_order=4,
        ),
        ClimaticIndicatorCreate(
            name="su30",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Summer days (SU30)",
            display_name_italian="Giorni caldi (SU30)",
            description_english=(
                "Number of days with maximum temperature larger than 30°C"
            ),
            description_italian=(
                "Numero di giorni con temperatura massima maggiore di 30°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="default/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=80,
            data_precision=0,
            sort_order=4,
        ),
        ClimaticIndicatorCreate(
            name="su30",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Summer days (SU30)",
            display_name_italian="Giorni caldi (SU30)",
            description_english=(
                "Number of days with maximum temperature larger than 30°C"
            ),
            description_italian=(
                "Numero di giorni con temperatura massima maggiore di 30°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="uncert-stippled/seq-YlOrRd",
            color_scale_min=-5,
            color_scale_max=75,
            data_precision=0,
            sort_order=4,
        ),
    ]
