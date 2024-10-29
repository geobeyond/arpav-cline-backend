from ...schemas.static import (
    AggregationPeriod,
    MeasureType,
)
from ...schemas.climaticindicators import ClimaticIndicatorCreate


def generate_climatic_indicators() -> list[ClimaticIndicatorCreate]:
    return [
        ClimaticIndicatorCreate(
            name="hwdi",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Heat waves duration index (HWDI)",
            display_name_italian="Durata delle ondate di calore (HWDI)",
            description_english=(
                "Number of days in which the maximum temperature is 5°C "
                "higher than the average for at least 5 consecutive days"
            ),
            description_italian=(
                "Numero di giorni in cui la temperatura massima è maggiore "
                "di 5°C rispetto alla media per  almeno 5 giorni consecutivi"
            ),
            unit_english="days",
            unit_italian="gg",
            palette="uncert-stippled/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=50,
            data_precision=0,
            sort_order=6,
        ),
    ]
