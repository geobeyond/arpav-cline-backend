import datetime as dt
from typing import Optional
import uuid

import sqlmodel

from ...schemas.base import (
    ObservationAggregationType,
    Season,
)


class ConfigurationParameterValueRead(sqlmodel.SQLModel):
    id: uuid.UUID
    internal_value: str
    name: str
    display_name_english: Optional[str]
    display_name_italian: Optional[str]
    description_english: Optional[str]
    description_italian: Optional[str]
    sort_order: int


class ConfigurationParameterRead(sqlmodel.SQLModel):
    id: uuid.UUID
    name: str
    display_name_english: Optional[str]
    display_name_italian: Optional[str]
    description_english: Optional[str]
    description_italian: Optional[str]
    allowed_values: list[ConfigurationParameterValueRead]


class ConfigurationParameterPossibleValueRead(sqlmodel.SQLModel):
    configuration_parameter_value_id: uuid.UUID
    configuration_parameter_value_name: str


class RelatedCoverageConfigurationRead(sqlmodel.SQLModel):
    id: uuid.UUID
    name: str


class CoverageConfigurationRead(sqlmodel.SQLModel):
    id: uuid.UUID
    name: str
    display_name_english: Optional[str]
    display_name_italian: Optional[str]
    description_english: Optional[str]
    description_italian: Optional[str]
    netcdf_main_dataset_name: str
    wms_main_layer_name: str
    wms_secondary_layer_name: Optional[str]
    coverage_id_pattern: str
    thredds_url_pattern: str
    unit_english: str
    unit_italian: str
    palette: str
    color_scale_min: float
    color_scale_max: float
    data_precision: int
    possible_values: list[ConfigurationParameterPossibleValueRead]
    observation_variable_aggregation_type: ObservationAggregationType
    observation_variable: Optional["ObservationVariableRead"]
    uncertainty_lower_bounds_coverage_configuration: Optional[
        "CoverageConfigurationReadListItem"
    ]
    uncertainty_upper_bounds_coverage_configuration: Optional[
        "CoverageConfigurationReadListItem"
    ]
    related_coverages: list[RelatedCoverageConfigurationRead]


class ObservationVariableRead(sqlmodel.SQLModel):
    id: uuid.UUID
    name: str


class CoverageConfigurationReadListItem(sqlmodel.SQLModel):
    id: uuid.UUID
    name: str


class VariableRead(sqlmodel.SQLModel):
    id: uuid.UUID
    name: str
    display_name_english: Optional[str]
    display_name_italian: Optional[str]
    description_english: Optional[str]
    description_italian: Optional[str]
    unit_english: Optional[str]
    unit_italian: Optional[str]


class StationRead(sqlmodel.SQLModel):
    id: uuid.UUID
    name: str
    code: str
    type: str
    longitude: float
    latitude: float
    active_since: Optional[dt.date]
    active_until: Optional[dt.date]
    altitude_m: Optional[float]


class MonthlyMeasurementRead(sqlmodel.SQLModel):
    station: str
    variable: str
    date: dt.date
    value: float


class SeasonalMeasurementRead(sqlmodel.SQLModel):
    station: str
    variable: str
    year: int
    season: Season
    value: float


class YearlyMeasurementRead(sqlmodel.SQLModel):
    station: str
    variable: str
    year: int
    value: float
