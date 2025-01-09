from ...schemas.static import (
    AggregationPeriod,
    MeasureType,
    ObservationStationManager,
)
from ...schemas.climaticindicators import (
    ClimaticIndicatorCreate,
    ClimaticIndicatorObservationNameCreate,
)


def generate_climatic_indicators() -> list[ClimaticIndicatorCreate]:
    return [
        ClimaticIndicatorCreate(
            name="pr",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Precipitation (PR)",
            display_name_italian="Precipitazione (PR)",
            description_english=("Daily precipitation near the ground"),
            description_italian=("Precipitazione giornaliera vicino al suolo"),
            unit_english="%",
            unit_italian="%",
            palette="default/div-BrBG",
            color_scale_min=-40,
            color_scale_max=40,
            data_precision=0,
            sort_order=9,
        ),
        ClimaticIndicatorCreate(
            name="pr",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Precipitation (PR)",
            display_name_italian="Precipitazione (PR)",
            description_english=("Daily precipitation near the ground"),
            description_italian=("Precipitazione giornaliera vicino al suolo"),
            unit_english="%",
            unit_italian="%",
            palette="uncert-stippled/div-BrBG",
            color_scale_min=-40,
            color_scale_max=40,
            data_precision=0,
            sort_order=9,
        ),
        ClimaticIndicatorCreate(
            name="pr",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Precipitation (PR)",
            display_name_italian="Precipitazione (PR)",
            description_english=("Daily precipitation near the ground"),
            description_italian=("Precipitazione giornaliera vicino al suolo"),
            unit_english="mm",
            unit_italian="mm",
            palette="default/seq-BuYl-inv",
            color_scale_min=0,
            color_scale_max=800,
            data_precision=0,
            sort_order=9,
            observation_names=[
                ClimaticIndicatorObservationNameCreate(
                    observation_station_manager=ObservationStationManager.ARPAV,
                    indicator_observation_name="PRCPTOT",
                )
            ],
        ),
        ClimaticIndicatorCreate(
            name="pr",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Precipitation (PR)",
            display_name_italian="Precipitazione (PR)",
            description_english=("Daily precipitation near the ground"),
            description_italian=("Precipitazione giornaliera vicino al suolo"),
            unit_english="mm",
            unit_italian="mm",
            palette="default/seq-YlOrRd",
            color_scale_min=300,
            color_scale_max=1300,
            data_precision=0,
            sort_order=9,
        ),
    ]
