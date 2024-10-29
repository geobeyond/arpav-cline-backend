from ...schemas.static import (
    AggregationPeriod,
    MeasureType,
)
from ...schemas.climaticindicators import ClimaticIndicatorCreate


def generate_climatic_indicators() -> list[ClimaticIndicatorCreate]:
    return [
        ClimaticIndicatorCreate(
            name="r95ptot",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Extreme precipitation (R95pTOT)",
            display_name_italian="Precipitazione estrema (R95pTOT)",
            description_english=(
                "Total cumulative precipitation above the 95th percentile "
                "with respect to the reference period"
            ),
            description_italian=(
                "Precipitazione totale cumulata al di sopra del 95o "
                "percentile del periodo di riferimento"
            ),
            unit_english="%",
            unit_italian="%",
            palette="uncert-stippled/div-BrBG",
            color_scale_min=-160,
            color_scale_max=160,
            data_precision=0,
            sort_order=10,
        ),
    ]
