import pydantic

from ..schemas import base, observations


class StationRead(observations.StationBase):
    ...


class StationCreate(observations.StationCreate):
    ...


class StationUpdate(observations.StationUpdate):
    ...


class VariableRead(observations.VariableBase):
    ...


class VariableCreate(observations.VariableCreate):
    ...


class VariableUpdate(observations.VariableUpdate):
    ...


class MonthlyMeasurementRead(observations.MonthlyMeasurementBase):
    station_id: pydantic.UUID4
    variable_id: pydantic.UUID4


# TODO: remove this
class MonthlyMeasurementCreate(observations.MonthlyMeasurementCreate):
    ...


# TODO: remove this
class MonthlyMeasurementUpdate(observations.MonthlyMeasurementUpdate):
    ...


class SeasonalMeasurementRead(pydantic.BaseModel):
    station_id: pydantic.UUID4
    variable_id: pydantic.UUID4
    year: int
    season: base.Season
    value: float


class YearlyMeasurementRead(pydantic.BaseModel):
    station_id: pydantic.UUID4
    variable_id: pydantic.UUID4
    year: int
    value: float
