from ...schemas.static import (
    AggregationPeriod,
    MeasureType,
)
from ...schemas.climaticindicators import ClimaticIndicatorCreate


def generate_climatic_indicators() -> list[ClimaticIndicatorCreate]:
    return [
        ClimaticIndicatorCreate(
            name="tr",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Tropical nights (TR)",
            display_name_italian="Notti tropicali (TR)",
            description_english=(
                "Number of days with minimum temperature larger than 20°C"
            ),
            description_italian=(
                "Numero di giorni con temperatura minima maggiore di 20°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="default/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=120,
            data_precision=1,
            sort_order=3,
        ),
        ClimaticIndicatorCreate(
            name="tr",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Tropical nights (TR)",
            display_name_italian="Notti tropicali (TR)",
            description_english=(
                "Number of days with minimum temperature larger than 20°C"
            ),
            description_italian=(
                "Numero di giorni con temperatura minima maggiore di 20°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="default/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=50,
            data_precision=1,
            sort_order=3,
        ),
        ClimaticIndicatorCreate(
            name="tr",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Tropical nights (TR)",
            display_name_italian="Notti tropicali (TR)",
            description_english=(
                "Number of days with minimum temperature larger than 20°C"
            ),
            description_italian=(
                "Numero di giorni con temperatura minima maggiore di 20°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="uncert-stippled/seq-YlOrRd",
            color_scale_min=-5,
            color_scale_max=75,
            data_precision=1,
            sort_order=3,
        ),
    ]
