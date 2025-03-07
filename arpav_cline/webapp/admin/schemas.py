import datetime as dt
from typing import Optional

import pydantic
import sqlmodel

from ...schemas.static import (
    AggregationPeriod,
    ForecastScenario,
    ForecastYearPeriod,
    HistoricalDecade,
    HistoricalReferencePeriod,
    HistoricalYearPeriod,
    MeasurementAggregationType,
    MeasureType,
    ObservationStationManager,
)


class ClimaticIndicatorObservationNameRead(sqlmodel.SQLModel):
    station_manager: ObservationStationManager
    indicator_observation_name: str


class ClimaticIndicatorForecastModelBasePathRead(sqlmodel.SQLModel):
    forecast_model: int
    thredds_url_base_path: str
    thredds_url_uncertainties_base_path: Optional[str] = None


class ClimaticIndicatorRead(sqlmodel.SQLModel):
    identifier: str
    id: int
    name: str
    historical_coverages_internal_name: Optional[str] = None
    measure_type: MeasureType
    aggregation_period: AggregationPeriod
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


class ObservationStationRead(sqlmodel.SQLModel):
    id: int
    name: str
    managed_by: ObservationStationManager
    longitude: float
    latitude: float
    code: str
    altitude_m: Optional[float]
    active_since: Optional[dt.date]
    active_until: Optional[dt.date]


class ObservationSeriesConfigurationRead(sqlmodel.SQLModel):
    id: int
    identifier: str
    measurement_aggregation_type: MeasurementAggregationType
    station_managers: list[ObservationStationManager]
    climatic_indicator: int


class ObservationMeasurementRead(sqlmodel.SQLModel):
    observation_station: int
    climatic_indicator: int
    measurement_aggregation_type: MeasurementAggregationType
    date: dt.date
    value: float


class ObservationOverviewSeriesConfigurationRead(sqlmodel.SQLModel):
    id: int
    identifier: str
    netcdf_main_dataset_name: str
    thredds_url_pattern: str
    climatic_indicator: Optional[int]


class ForecastModelGroupRead(sqlmodel.SQLModel):
    id: int
    name: str
    display_name_english: str
    display_name_italian: str
    description_english: str
    description_italian: str
    sort_order: int
    forecast_models: list[int]


class ForecastYearPeriodGroupRead(sqlmodel.SQLModel):
    id: int
    name: str
    display_name_english: str
    display_name_italian: str
    description_english: str
    description_italian: str
    sort_order: int
    year_periods: list[ForecastYearPeriod]


class HistoricalYearPeriodGroupRead(sqlmodel.SQLModel):
    id: int
    name: str
    display_name_english: str
    display_name_italian: str
    description_english: str
    description_italian: str
    sort_order: int
    year_periods: list[HistoricalYearPeriod]


class ForecastOverviewSeriesConfigurationRead(sqlmodel.SQLModel):
    id: int
    identifier: str
    netcdf_main_dataset_name: str
    thredds_url_pattern: str
    climatic_indicator: Optional[int]
    lower_uncertainty_thredds_url_pattern: Optional[str]
    lower_uncertainty_netcdf_main_dataset_name: Optional[str]
    upper_uncertainty_thredds_url_pattern: Optional[str]
    upper_uncertainty_netcdf_main_dataset_name: Optional[str]
    scenarios: list[ForecastScenario]


class HistoricalCoverageConfigurationRead(sqlmodel.SQLModel):
    id: int
    identifier: str
    netcdf_main_dataset_name: str
    thredds_url_pattern: str
    wms_main_layer_name: str
    year_period_group: int
    climatic_indicator: Optional[int]
    spatial_region: Optional[int]
    reference_period: Optional[HistoricalReferencePeriod]
    decades: list[HistoricalDecade]
    observation_series_configurations: list[int]


class ForecastCoverageConfigurationRead(sqlmodel.SQLModel):
    id: int
    identifier: str
    netcdf_main_dataset_name: str
    thredds_url_pattern: str
    wms_main_layer_name: str
    wms_secondary_layer_name: Optional[str]
    climatic_indicator: Optional[int]
    spatial_region: Optional[int]
    year_period_group: int
    forecast_model_group: int
    lower_uncertainty_thredds_url_pattern: Optional[str]
    lower_uncertainty_netcdf_main_dataset_name: Optional[str]
    upper_uncertainty_thredds_url_pattern: Optional[str]
    upper_uncertainty_netcdf_main_dataset_name: Optional[str]
    scenarios: list[ForecastScenario]
    time_windows: list[int]
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


class ForecastCoverageDownloadRequestRead(sqlmodel.SQLModel):
    id: int
    request_datetime: dt.datetime
    entity_name: str | None
    is_public_sector: bool
    download_reason: str
    climatological_variable: str
    aggregation_period: str
    measure_type: str
    year_period: str
    climatological_model: str
    scenario: str
    time_window: str | None


class HistoricalCoverageDownloadRequestRead(sqlmodel.SQLModel):
    id: int
    request_datetime: dt.datetime
    entity_name: str | None
    is_public_sector: bool
    download_reason: str
    climatological_variable: str
    aggregation_period: str
    measure_type: str
    year_period: str
    decade: str | None
    reference_period: str | None


class TimeSeriesDownloadRequestRead(sqlmodel.SQLModel):
    id: int
    request_datetime: dt.datetime
    entity_name: str | None
    is_public_sector: bool
    download_reason: str
    climatological_variable: str
    aggregation_period: str
    measure_type: str
    year_period: str
    data_category: str
    longitude: float
    latitude: float
