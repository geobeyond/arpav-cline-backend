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
            name="tasmax",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Maximum temperature (TASMAX)",
            display_name_italian="Temperatura massima (TASMAX)",
            description_english=("Daily maximum air temperature close to the ground"),
            description_italian=(
                "Temperatura massima giornaliera dell'aria vicino al suolo"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/seq-YlOrRd",
            color_scale_min=-3,
            color_scale_max=32,
            data_precision=1,
            sort_order=2,
            observation_names=[
                ClimaticIndicatorObservationNameCreate(
                    observation_station_manager=ObservationStationManager.ARPAV,
                    indicator_observation_name="TXd",
                )
            ],
        ),
        ClimaticIndicatorCreate(
            name="tasmax",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Maximum temperature (TASMAX)",
            display_name_italian="Temperatura massima (TASMAX)",
            description_english=("Daily maximum air temperature close to the ground"),
            description_italian=(
                "Temperatura massima giornaliera dell'aria vicino al suolo"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/seq-YlOrRd",
            color_scale_min=-5,
            color_scale_max=20,
            data_precision=1,
            sort_order=2,
        ),
        ClimaticIndicatorCreate(
            name="tasmax",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Maximum temperature (TASMAX)",
            display_name_italian="Temperatura massima (TASMAX)",
            description_english=("Daily maximum air temperature close to the ground"),
            description_italian=(
                "Temperatura massima giornaliera dell'aria vicino al suolo"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="uncert-stippled/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=6,
            data_precision=1,
            sort_order=2,
        ),
    ]
