import pydantic

from ..schemas import (
    observations,
    static,
)


class OverviewCoverageConfigurationItem(pydantic.BaseModel):
    identifier: str


class ClimaticIndicatorItem(pydantic.BaseModel):
    identifier: str


class ClimaticIndicatorDetail(pydantic.BaseModel):
    identifier: str
    name: str
    measure_type: static.MeasureType
    aggregation_period: static.AggregationPeriod
    display_name_english: str
    description_english: str
    unit_english: str
    palette: str
    color_scale_min: float
    color_scale_max: float
    data_precision: float


class ObservationStationItem(pydantic.BaseModel):
    managed_by: str
    code: str
    name: str


class ObservationStationDetail(observations.StationBase):
    code: str
    name: str


class ObservationSeriesConfigurationItem(pydantic.BaseModel):
    climatic_indicator: str
    station_managers: list[str]
    measurement_aggregation_type: static.MeasurementAggregationType
    identifier: str


class ObservationSeriesConfigurationDetail(pydantic.BaseModel):
    identifier: str
    climatic_indicator: ClimaticIndicatorItem
    measurement_aggregation_type: static.MeasurementAggregationType
    station_managers: list[static.ObservationStationManager]
