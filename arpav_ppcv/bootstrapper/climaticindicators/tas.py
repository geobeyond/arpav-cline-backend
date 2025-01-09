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
            name="tas",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Average temperature (TAS)",
            display_name_italian="Temperatura media (TAS)",
            description_english="Daily mean air temperature close to the ground",
            description_italian="Temperatura media giornaliera dell'aria vicino al suolo",
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/seq-YlOrRd",
            color_scale_min=-3,
            color_scale_max=32,
            data_precision=1,
            sort_order=0,
            observation_names=[
                ClimaticIndicatorObservationNameCreate(
                    observation_station_manager=ObservationStationManager.ARPAV,
                    indicator_observation_name="TDd",
                )
            ],
        ),
        ClimaticIndicatorCreate(
            name="tas",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Average temperature (TAS)",
            display_name_italian="Temperatura media (TAS)",
            description_english="Daily mean air temperature close to the ground",
            description_italian="Temperatura media giornaliera dell'aria vicino al suolo",
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/seq-YlOrRd",
            color_scale_min=-5,
            color_scale_max=20,
            data_precision=1,
            sort_order=0,
        ),
        ClimaticIndicatorCreate(
            name="tas",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Average temperature (TAS)",
            display_name_italian="Temperatura media (TAS)",
            description_english="Daily mean air temperature close to the ground",
            description_italian="Temperatura media giornaliera dell'aria vicino al suolo",
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=6,
            data_precision=1,
            sort_order=0,
        ),
        ClimaticIndicatorCreate(
            name="tas",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Average temperature (TAS)",
            display_name_italian="Temperatura media (TAS)",
            description_english="Daily mean air temperature close to the ground",
            description_italian="Temperatura media giornaliera dell'aria vicino al suolo",
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/seq-YlOrRd",
            color_scale_min=0,
            color_scale_max=6,
            data_precision=1,
            sort_order=0,
        ),
    ]
