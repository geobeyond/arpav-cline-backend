from ...schemas.static import (
    AggregationPeriod,
    MeasureType,
)
from ...schemas.climaticindicators import ClimaticIndicatorCreate


def generate_climatic_indicators() -> list[ClimaticIndicatorCreate]:
    return [
        ClimaticIndicatorCreate(
            name="snwdays",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Snow days (SNWDAYS)",
            display_name_italian="Giorni con neve nuova (SNWDAYS)",
            description_english=(
                "Number of days with average temperature less than 2°C and "
                "daily precipitation larger than 1 mm"
            ),
            description_italian=(
                "Numero di giorni con temperatura media minore di 2°C e "
                "precipitazione giornaliera maggiore di 1 mm"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="default/seq-BuYl-inv",
            color_scale_min=0,
            color_scale_max=100,
            data_precision=0,
            sort_order=12,
        ),
        ClimaticIndicatorCreate(
            name="snwdays",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Snow days (SNWDAYS)",
            display_name_italian="Giorni con neve nuova (SNWDAYS)",
            description_english=(
                "Number of days with average temperature less than 2°C and "
                "daily precipitation larger than 1 mm"
            ),
            description_italian=(
                "Numero di giorni con temperatura media minore di 2°C e "
                "precipitazione giornaliera maggiore di 1 mm"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="uncert-stippled/seq-YlOrBr-inv",
            color_scale_min=-50,
            color_scale_max=50,
            data_precision=0,
            sort_order=12,
        ),
    ]
