from ...schemas.static import (
    AggregationPeriod,
    MeasureType,
)
from ...schemas.climaticindicators import ClimaticIndicatorCreate


def generate_climatic_indicators() -> list[ClimaticIndicatorCreate]:
    return [
        ClimaticIndicatorCreate(
            name="cdd",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Consecutive dry days (CDD)",
            display_name_italian="Giorni secchi (CDD)",
            description_english=(
                "Maximum number of consecutive dry days (daily precipitation "
                "less than 1 mm)"
            ),
            description_italian=(
                "Numero massimo di giorni consecutivi asciutti "
                "(precipitazione giornaliera inferiore a 1 mm)"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="uncert-stippled/div-BrBG-inv",
            color_scale_min=-40,
            color_scale_max=40,
            data_precision=0,
            sort_order=11,
        ),
    ]
