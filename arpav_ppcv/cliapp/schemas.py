import pydantic

from ..schemas import (
    observations,
    static,
)


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
    indicator_internal_name: str


class ObservationSeriesConfigurationDetail(pydantic.BaseModel):
    identifier: str
    climatic_indicator: ClimaticIndicatorItem
    indicator_internal_name: str
    measurement_aggregation_type: static.MeasurementAggregationType
    station_managers: list[static.ObservationStationManager]


class ObservationStationCreate(observations.StationCreate):
    ...


class ObservationStationUpdate(observations.StationUpdate):
    ...


# class VariableRead(observations.VariableBase):
#     ...
#
#
# class VariableCreate(observations.VariableCreate):
#     ...
#
#
# class VariableUpdate(observations.VariableUpdate):
#     ...


# class MonthlyMeasurementRead(observations.MonthlyMeasurementBase):
#     station_id: pydantic.UUID4
#     variable_id: pydantic.UUID4
#
#
# # TODO: remove this
# class MonthlyMeasurementCreate(observations.MonthlyMeasurementCreate):
#     ...
#
#
# # TODO: remove this
# class MonthlyMeasurementUpdate(observations.MonthlyMeasurementUpdate):
#     ...
#
#
# class SeasonalMeasurementRead(pydantic.BaseModel):
#     station_id: pydantic.UUID4
#     variable_id: pydantic.UUID4
#     year: int
#     season: base.Season
#     value: float
#
#
# class YearlyMeasurementRead(pydantic.BaseModel):
#     station_id: pydantic.UUID4
#     variable_id: pydantic.UUID4
#     year: int
#     value: float
