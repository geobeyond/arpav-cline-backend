import datetime as dt
from typing import Optional
import uuid

import pydantic
import sqlmodel

from ...schemas.base import ObservationAggregationType
from ...schemas import static


class ClimaticIndicatorObservationNameRead(sqlmodel.SQLModel):
    station_manager: static.ObservationStationManager
    indicator_observation_name: str


class ClimaticIndicatorForecastModelBasePathRead(sqlmodel.SQLModel):
    forecast_model: int
    thredds_url_base_path: str


class ClimaticIndicatorRead(sqlmodel.SQLModel):
    identifier: str
    id: int
    name: str
    measure_type: static.MeasureType
    aggregation_period: static.AggregationPeriod
    display_name_english: str
    display_name_italian: str
    description_english: str
    description_italian: str
    unit_english: str
    unit_italian: str
    palette: str
    color_scale_min: float
    color_scale_max: float
    data_precision: int
    sort_order: int
    observation_names: list[ClimaticIndicatorObservationNameRead]
    forecast_model_base_paths: list[ClimaticIndicatorForecastModelBasePathRead]


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
    # display_name_english: Optional[str]
    # display_name_italian: Optional[str]
    # description_english: Optional[str]
    # description_italian: Optional[str]
    netcdf_main_dataset_name: str
    wms_main_layer_name: str
    wms_secondary_layer_name: Optional[str]
    coverage_id_pattern: str
    thredds_url_pattern: str
    # unit_english: str
    # unit_italian: str
    # palette: str
    # color_scale_min: float
    # color_scale_max: float
    # data_precision: int
    climatic_indicator: Optional[int]
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


class ObservationStationRead(sqlmodel.SQLModel):
    id: int
    name: str
    managed_by: static.ObservationStationManager
    longitude: float
    latitude: float
    code: str
    altitude_m: Optional[float]
    active_since: Optional[dt.date]
    active_until: Optional[dt.date]


class ObservationSeriesConfigurationRead(sqlmodel.SQLModel):
    id: int
    identifier: str
    measurement_aggregation_type: static.MeasurementAggregationType
    station_managers: list[static.ObservationStationManager]
    climatic_indicator: int


class ObservationMeasurementRead(sqlmodel.SQLModel):
    observation_station: int
    climatic_indicator: int
    measurement_aggregation_type: static.MeasurementAggregationType
    date: dt.date
    value: float


class ForecastCoverageConfigurationRead(sqlmodel.SQLModel):
    id: int
    identifier: str
    netcdf_main_dataset_name: str
    thredds_url_pattern: str
    wms_main_layer_name: str
    wms_secondary_layer_name: Optional[str]
    climatic_indicator: Optional[int]
    spatial_region: Optional[int]
    lower_uncertainty_thredds_url_pattern: Optional[str]
    lower_uncertainty_netcdf_main_dataset_name: Optional[str]
    upper_uncertainty_thredds_url_pattern: Optional[str]
    upper_uncertainty_netcdf_main_dataset_name: Optional[str]
    scenarios: list[static.ForecastScenario]
    year_periods: list[static.ForecastYearPeriod]
    forecast_models: list[int]
    forecast_time_windows: list[int]
    observation_series_configurations: list[int]


class ForecastModelRead(sqlmodel.SQLModel):
    id: int
    name: str
    internal_value: str
    display_name_english: str
    display_name_italian: str
    description_english: str
    description_italian: str
    sort_order: int


class ForecastTimeWindowRead(sqlmodel.SQLModel):
    id: int
    name: str
    internal_value: str
    display_name_english: str
    display_name_italian: str
    description_english: str
    description_italian: str
    sort_order: int


class SpatialRegionRead(sqlmodel.SQLModel):
    id: int
    name: str
    display_name_english: str
    display_name_italian: str
    sort_order: int
    geom: pydantic.Json


#
# class StationRead(sqlmodel.SQLModel):
#     id: uuid.UUID
#     name: str
#     code: str
#     type: str
#     longitude: float
#     latitude: float
#     active_since: Optional[dt.date]
#     active_until: Optional[dt.date]
#     altitude_m: Optional[float]
#
#
# class MonthlyMeasurementRead(sqlmodel.SQLModel):
#     station: str
#     variable: str
#     date: dt.date
#     value: float
#
#
# class SeasonalMeasurementRead(sqlmodel.SQLModel):
#     station: str
#     variable: str
#     year: int
#     season: Season
#     value: float
#
#
# class YearlyMeasurementRead(sqlmodel.SQLModel):
#     station: str
#     variable: str
#     year: int
#     value: float
