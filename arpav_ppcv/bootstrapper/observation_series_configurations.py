from ..schemas.climaticindicators import ClimaticIndicator
from ..schemas.observations import ObservationSeriesConfigurationCreate
from ..schemas.static import (
    MeasurementAggregationType,
    ObservationStationManager,
)


def generate_observation_series_configurations(
    indicators: dict[str, ClimaticIndicator],
) -> list[ObservationSeriesConfigurationCreate]:
    return [
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["hdds-absolute-annual"].id,
            measurement_aggregation_type=MeasurementAggregationType.YEARLY,
            station_managers=[ObservationStationManager.ARPAV],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["cdds-absolute-annual"].id,
            measurement_aggregation_type=MeasurementAggregationType.YEARLY,
            station_managers=[ObservationStationManager.ARPAV],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["tas-absolute-annual"].id,
            measurement_aggregation_type=MeasurementAggregationType.SEASONAL,
            station_managers=[ObservationStationManager.ARPAV],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["tas-absolute-annual"].id,
            measurement_aggregation_type=MeasurementAggregationType.YEARLY,
            station_managers=[ObservationStationManager.ARPAV],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["tasmax-absolute-annual"].id,
            measurement_aggregation_type=MeasurementAggregationType.SEASONAL,
            station_managers=[ObservationStationManager.ARPAV],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["tasmax-absolute-annual"].id,
            measurement_aggregation_type=MeasurementAggregationType.YEARLY,
            station_managers=[ObservationStationManager.ARPAV],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["tasmin-absolute-annual"].id,
            measurement_aggregation_type=MeasurementAggregationType.SEASONAL,
            station_managers=[ObservationStationManager.ARPAV],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["tasmin-absolute-annual"].id,
            measurement_aggregation_type=MeasurementAggregationType.YEARLY,
            station_managers=[ObservationStationManager.ARPAV],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["pr-absolute-annual"].id,
            measurement_aggregation_type=MeasurementAggregationType.SEASONAL,
            station_managers=[ObservationStationManager.ARPAV],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["pr-absolute-annual"].id,
            measurement_aggregation_type=MeasurementAggregationType.YEARLY,
            station_managers=[ObservationStationManager.ARPAV],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["tr-absolute-annual"].id,
            measurement_aggregation_type=MeasurementAggregationType.YEARLY,
            station_managers=[ObservationStationManager.ARPAV],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["su30-absolute-annual"].id,
            measurement_aggregation_type=MeasurementAggregationType.YEARLY,
            station_managers=[ObservationStationManager.ARPAV],
        ),
        ObservationSeriesConfigurationCreate(
            climatic_indicator_id=indicators["fd-absolute-annual"].id,
            measurement_aggregation_type=MeasurementAggregationType.YEARLY,
            station_managers=[ObservationStationManager.ARPAV],
        ),
    ]
