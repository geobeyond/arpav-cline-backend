from ...schemas.static import (
    AggregationPeriod,
    MeasureType,
)
from ...schemas.climaticindicators import ClimaticIndicatorCreate


def generate_climatic_indicators() -> list[ClimaticIndicatorCreate]:
    return [
        ClimaticIndicatorCreate(
            name="cdds",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Cooling degree days (CDDs)",
            display_name_italian="Gradi giorno di raffrescamento (CDDs)",
            description_english=(
                "Sum of the average daily temperature minus 21°C if the "
                "average daily temperature is larger than 24°C"
            ),
            description_italian=(
                "Somma della temperatura media giornaliera meno 21°C se la "
                "temperatura media giornaliera è maggiore di 24°C"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=1000,
            data_precision=0,
            sort_order=8,
        ),
        ClimaticIndicatorCreate(
            name="cdds",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Cooling degree days (CDDs)",
            display_name_italian="Gradi giorno di raffrescamento (CDDs)",
            description_english=(
                "Sum of the average daily temperature minus 21°C if the "
                "average daily temperature is larger than 24°C"
            ),
            description_italian=(
                "Somma della temperatura media giornaliera meno 21°C se la "
                "temperatura media giornaliera è maggiore di 24°C"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=320,
            data_precision=0,
            sort_order=8,
        ),
        ClimaticIndicatorCreate(
            name="cdds",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Cooling degree days (CDDs)",
            display_name_italian="Gradi giorno di raffrescamento (CDDs)",
            description_english=(
                "Sum of the average daily temperature minus 21°C if the "
                "average daily temperature is larger than 24°C"
            ),
            description_italian=(
                "Somma della temperatura media giornaliera meno 21°C se la "
                "temperatura media giornaliera è maggiore di 24°C"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="uncert-stippled/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=1000,
            data_precision=0,
            sort_order=8,
        ),
    ]
