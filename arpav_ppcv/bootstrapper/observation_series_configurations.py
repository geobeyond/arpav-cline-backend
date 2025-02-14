from ..schemas.observations import ObservationSeriesConfigurationCreate
from ..schemas.static import (
    MeasurementAggregationType,
    ObservationStationManager,
)


def generate_observation_series_configurations(
    indicators: dict[str, int],
) -> list[ObservationSeriesConfigurationCreate]:
    return [
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["hdds-absolute-annual"],
            measurement_aggregation_type=MeasurementAggregationType.YEARLY,
            station_managers=[ObservationStationManager.ARPAV],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["cdds-absolute-annual"],
            measurement_aggregation_type=MeasurementAggregationType.YEARLY,
            station_managers=[ObservationStationManager.ARPAV],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["fd-absolute-annual"],
            measurement_aggregation_type=MeasurementAggregationType.YEARLY,
            station_managers=[
                ObservationStationManager.ARPAV,
                ObservationStationManager.ARPAFVG,
            ],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["fd-absolute-annual"],
            measurement_aggregation_type=MeasurementAggregationType.SEASONAL,
            station_managers=[
                ObservationStationManager.ARPAV,
                ObservationStationManager.ARPAFVG,
            ],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["snwdays-absolute-annual"],
            measurement_aggregation_type=MeasurementAggregationType.YEARLY,
            station_managers=[ObservationStationManager.ARPAFVG],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["snwdays-absolute-annual"],
            measurement_aggregation_type=MeasurementAggregationType.SEASONAL,
            station_managers=[ObservationStationManager.ARPAFVG],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["su30-absolute-annual"],
            measurement_aggregation_type=MeasurementAggregationType.YEARLY,
            station_managers=[
                ObservationStationManager.ARPAV,
                ObservationStationManager.ARPAFVG,
            ],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["su30-absolute-annual"],
            measurement_aggregation_type=MeasurementAggregationType.SEASONAL,
            station_managers=[
                ObservationStationManager.ARPAV,
                ObservationStationManager.ARPAFVG,
            ],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["tas-absolute-annual"],
            measurement_aggregation_type=MeasurementAggregationType.SEASONAL,
            station_managers=[
                ObservationStationManager.ARPAV,
                ObservationStationManager.ARPAFVG,
            ],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["tas-absolute-annual"],
            measurement_aggregation_type=MeasurementAggregationType.YEARLY,
            station_managers=[
                ObservationStationManager.ARPAV,
                ObservationStationManager.ARPAFVG,
            ],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["tasmax-absolute-annual"],
            measurement_aggregation_type=MeasurementAggregationType.SEASONAL,
            station_managers=[
                ObservationStationManager.ARPAV,
                ObservationStationManager.ARPAFVG,
            ],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["tasmax-absolute-annual"],
            measurement_aggregation_type=MeasurementAggregationType.YEARLY,
            station_managers=[
                ObservationStationManager.ARPAV,
                ObservationStationManager.ARPAFVG,
            ],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["tasmin-absolute-annual"],
            measurement_aggregation_type=MeasurementAggregationType.SEASONAL,
            station_managers=[
                ObservationStationManager.ARPAV,
                ObservationStationManager.ARPAFVG,
            ],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["tasmin-absolute-annual"],
            measurement_aggregation_type=MeasurementAggregationType.YEARLY,
            station_managers=[
                ObservationStationManager.ARPAV,
                ObservationStationManager.ARPAFVG,
            ],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["pr-absolute-annual"],
            measurement_aggregation_type=MeasurementAggregationType.SEASONAL,
            station_managers=[
                ObservationStationManager.ARPAV,
                ObservationStationManager.ARPAFVG,
            ],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["pr-absolute-annual"],
            measurement_aggregation_type=MeasurementAggregationType.YEARLY,
            station_managers=[
                ObservationStationManager.ARPAV,
                ObservationStationManager.ARPAFVG,
            ],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["pr-absolute-annual"],
            measurement_aggregation_type=MeasurementAggregationType.MONTHLY,
            station_managers=[
                ObservationStationManager.ARPAV,
                ObservationStationManager.ARPAFVG,
            ],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["tr-absolute-annual"],
            measurement_aggregation_type=MeasurementAggregationType.YEARLY,
            station_managers=[
                ObservationStationManager.ARPAV,
                ObservationStationManager.ARPAFVG,
            ],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["tr-absolute-annual"],
            measurement_aggregation_type=MeasurementAggregationType.SEASONAL,
            station_managers=[
                ObservationStationManager.ARPAV,
                ObservationStationManager.ARPAFVG,
            ],
        ),
    ]
