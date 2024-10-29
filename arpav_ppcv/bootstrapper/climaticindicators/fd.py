from ...schemas.static import (
    AggregationPeriod,
    MeasureType,
)
from ...schemas.climaticindicators import ClimaticIndicatorCreate


def generate_climatic_indicators() -> list[ClimaticIndicatorCreate]:
    return [
        ClimaticIndicatorCreate(
            name="fd",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Frost days (FD)",
            display_name_italian="Giorni di gelo (FD)",
            description_english=(
                "Number of days with minimum temperature less than 0ºC"
            ),
            description_italian=(
                "Numero di giorni con temperatura minima minore di 0°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="default/seq-Blues-inv",
            color_scale_min=0,
            color_scale_max=200,
            data_precision=0,
            sort_order=5,
        ),
        ClimaticIndicatorCreate(
            name="fd",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Frost days (FD)",
            display_name_italian="Giorni di gelo (FD)",
            description_english=(
                "Number of days with minimum temperature less than 0ºC"
            ),
            description_italian=(
                "Numero di giorni con temperatura minima minore di 0°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="uncert-stippled/seq-YlOrRd-inv",
            color_scale_min=-85,
            color_scale_max=5,
            data_precision=0,
            sort_order=5,
        ),
        ClimaticIndicatorCreate(
            name="fd",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Frost days (FD)",
            display_name_italian="Giorni di gelo (FD)",
            description_english=(
                "Number of days with minimum temperature less than 0ºC"
            ),
            description_italian=(
                "Numero di giorni con temperatura minima minore di 0°C"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="default/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=260,
            data_precision=0,
            sort_order=5,
        ),
    ]
