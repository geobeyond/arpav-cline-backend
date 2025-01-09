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
            name="hdds",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.ANNUAL,
            display_name_english="Heating degree days (HDDs)",
            display_name_italian="Gradi giorno di riscaldamento (HDDs)",
            description_english=(
                "Sum of 20°C minus the average daily temperature if the "
                "average daily temperature is less than 20°C"
            ),
            description_italian=(
                "Somma di 20°C meno la temperatura media giornaliera se la "
                "temperatura media giornaliera è minore di 20°C"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/seq-Blues-inv",
            color_scale_min=0,
            color_scale_max=7000,
            data_precision=0,
            sort_order=7,
            observation_names=[
                ClimaticIndicatorObservationNameCreate(
                    observation_station_manager=ObservationStationManager.ARPAV,
                    indicator_observation_name="HDD_it",
                ),
            ],
        ),
        ClimaticIndicatorCreate(
            name="hdds",
            measure_type=MeasureType.ANOMALY,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Heating degree days (HDDs)",
            display_name_italian="Gradi giorno di riscaldamento (HDDs)",
            description_english=(
                "Sum of 20°C minus the average daily temperature if the "
                "average daily temperature is less than 20°C"
            ),
            description_italian=(
                "Somma di 20°C meno la temperatura media giornaliera se la "
                "temperatura media giornaliera è minore di 20°C"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/seq-Blues-inv",
            color_scale_min=-2000,
            color_scale_max=0,
            data_precision=0,
            sort_order=7,
        ),
        ClimaticIndicatorCreate(
            name="hdds",
            measure_type=MeasureType.ABSOLUTE,
            aggregation_period=AggregationPeriod.THIRTY_YEAR,
            display_name_english="Heating degree days (HDDs)",
            display_name_italian="Gradi giorno di riscaldamento (HDDs)",
            description_english=(
                "Sum of 20°C minus the average daily temperature if the "
                "average daily temperature is less than 20°C"
            ),
            description_italian=(
                "Somma di 20°C meno la temperatura media giornaliera se la "
                "temperatura media giornaliera è minore di 20°C"
            ),
            unit_english="ºC",
            unit_italian="ºC",
            palette="default/seq-YlOrRd",
            color_scale_min=2130,
            color_scale_max=7800,
            data_precision=0,
            sort_order=7,
        ),
    ]
