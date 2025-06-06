import datetime as dt
import dataclasses
from typing import (
    Optional,
    Protocol,
    TYPE_CHECKING,
    Union,
)

import geohashr
import pandas as pd
import pydantic
import shapely.io
import typing_extensions
from geoalchemy2.shape import to_shape

from ..config import get_translations
from . import static

if TYPE_CHECKING:
    import babel
    from .observations import (
        ObservationSeriesConfiguration,
        ObservationStation,
    )
    from .overviews import (
        ForecastOverviewSeriesInternal,
        ObservationOverviewSeriesInternal,
    )
    from .static import (
        StaticForecastCoverage,
        StaticForecastOverviewSeries,
        StaticHistoricalCoverage,
        StaticHistoricalOverviewSeries,
    )


class MannKendallParameters(pydantic.BaseModel):
    start_year: int | None = None
    end_year: int | None = None

    @pydantic.model_validator(mode="after")
    def check_year_span_is_valid(self) -> typing_extensions.Self:
        if self.start_year is not None and self.end_year is not None:
            if self.end_year - self.start_year < 27:
                raise ValueError(
                    "Mann-Kendall start and end years must span 27 years or more"
                )
        return self


class OverviewDataSeriesProtocol(Protocol):
    overview_series: Union[
        "ForecastOverviewSeriesInternal", "ObservationOverviewSeriesInternal"
    ]
    dataset_type: static.DatasetType
    processing_method: static.CoverageTimeSeriesProcessingMethod
    data_: Optional[pd.Series]

    @property
    def identifier(self) -> str:
        return NotImplemented

    @staticmethod
    def get_display_name(locale: "babel.Locale") -> str:
        return NotImplemented

    @staticmethod
    def get_description(locale: "babel.Locale") -> str:
        return NotImplemented

    def replace(self, **kwargs) -> "OverviewDataSeriesProtocol":
        return NotImplemented


@dataclasses.dataclass
class ObservationOverviewDataSeries:
    overview_series: "StaticHistoricalOverviewSeries"
    dataset_type: static.DatasetType
    processing_method: static.CoverageTimeSeriesProcessingMethod
    data_: Optional[pd.Series] = None

    @property
    def identifier(self) -> str:
        return "-".join(
            (
                self.overview_series.identifier,
                self.dataset_type.value,
                self.processing_method.value,
            )
        )

    @staticmethod
    def get_display_name(locale: "babel.Locale") -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("observation overview data series")

    @staticmethod
    def get_description(locale: "babel.Locale") -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("observation overview data series description")

    def replace(self, *args, **kwargs) -> "ObservationOverviewDataSeries":
        return dataclasses.replace(self, **kwargs)


@dataclasses.dataclass
class ForecastOverviewDataSeries:
    overview_series: "StaticForecastOverviewSeries"
    processing_method: static.CoverageTimeSeriesProcessingMethod
    dataset_type: static.DatasetType
    data_: Optional[pd.Series] = None

    @property
    def identifier(self) -> str:
        return "-".join(
            (
                self.overview_series.identifier,
                self.dataset_type.value,
                self.processing_method.value,
            )
        )

    @staticmethod
    def get_display_name(locale: "babel.Locale") -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("forecast overview data series")

    @staticmethod
    def get_description(locale: "babel.Locale") -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("forecast overview data series description")

    def replace(self, *args, **kwargs) -> "ForecastOverviewDataSeries":
        return dataclasses.replace(self, **kwargs)


@dataclasses.dataclass
class ForecastDataSeries:
    coverage: "StaticForecastCoverage"
    dataset_type: static.DatasetType
    location: shapely.Point
    processing_method: static.CoverageTimeSeriesProcessingMethod
    temporal_end: Optional[dt.date]
    temporal_start: Optional[dt.date]
    data_: Optional[pd.Series] = None
    processing_method_info: Optional[dict] = None

    @property
    def identifier(self) -> str:
        return "-".join(
            (
                self.coverage.coverage_identifier,
                self.dataset_type.value,
                geohashr.encode(self.location.x, self.location.y),
                (
                    self.temporal_start.strftime("%Y%m%d")
                    if self.temporal_start is not None
                    else "*"
                ),
                (
                    self.temporal_end.strftime("%Y%m%d")
                    if self.temporal_end is not None
                    else "*"
                ),
                self.processing_method.value,
            )
        )

    @staticmethod
    def get_display_name(locale: "babel.Locale") -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("forecast data series")

    @staticmethod
    def get_description(locale: "babel.Locale") -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("forecast data series description")

    def get_legacy_info(self) -> dict:
        return {
            "coverage_identifier": self.coverage.coverage_identifier,
            "dataset_type": self.dataset_type,
            "coverage_configuration": self.coverage.coverage_configuration_identifier,
            "aggregation_period": self.coverage.aggregation_period.value,
            "climatological_model": self.coverage.forecast_model_name,
            "climatological_variable": self.coverage.climatic_indicator_name,
            "measure": self.coverage.measure_type.value,
            "scenario": self.coverage.scenario.value,
            "year_period": self.coverage.year_period.value,
            "processing_method": self.processing_method.value,
            "processing_method_info": self.processing_method_info,
            "location": self.location.wkt,
        }


@dataclasses.dataclass
class ObservationStationDataSeries:
    observation_series_configuration: "ObservationSeriesConfiguration"
    observation_station: "ObservationStation"
    dataset_type: static.DatasetType
    processing_method: static.HistoricalTimeSeriesProcessingMethod
    location: shapely.Point
    processing_method_info: Optional[dict] = None
    data_: Optional[pd.Series] = None

    @property
    def identifier(self) -> str:
        return "-".join(
            (
                "station",
                self.observation_station.code,
                self.observation_series_configuration.identifier,
                self.processing_method.value,
            )
        )

    @staticmethod
    def get_display_name(locale: "babel.Locale") -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("observation station data series")

    @staticmethod
    def get_description(locale: "babel.Locale") -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("observation station data series description")

    def get_legacy_info(self) -> dict:
        return {
            "series_identifier": self.observation_series_configuration.identifier,
            "aggregation_period": (
                self.observation_series_configuration.climatic_indicator.aggregation_period.value
            ),
            "dataset_type": self.dataset_type,
            "climatological_variable": self.observation_series_configuration.climatic_indicator.name,
            "measure": self.observation_series_configuration.climatic_indicator.measure_type.value,
            "measurement_aggregation_type": self.observation_series_configuration.measurement_aggregation_type.value,
            "processing_method": self.processing_method.value,
            "processing_method_info": self.processing_method_info,
            "manager": self.observation_station.managed_by.name,
            "location": self.location.wkt,
            "station_location": to_shape(self.observation_station.geom).wkt,
            "station_name": self.observation_station.name,
            "station_code": self.observation_station.code,
        }


@dataclasses.dataclass
class HistoricalDataSeries:
    coverage: "StaticHistoricalCoverage"
    dataset_type: static.DatasetType
    location: shapely.Point
    processing_method: static.HistoricalTimeSeriesProcessingMethod
    temporal_end: Optional[dt.date]
    temporal_start: Optional[dt.date]
    data_: Optional[pd.Series] = None
    processing_method_info: Optional[dict] = None

    @property
    def identifier(self) -> str:
        return "-".join(
            (
                self.coverage.coverage_identifier,
                self.dataset_type.value,
                geohashr.encode(self.location.x, self.location.y),
                self.processing_method.value,
            )
        )

    @staticmethod
    def get_display_name(locale: "babel.Locale") -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("historical data series")

    @staticmethod
    def get_description(locale: "babel.Locale") -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("historical data series description")

    def get_legacy_info(self) -> dict:
        info = {
            "coverage_identifier": self.coverage.coverage_identifier,
            "coverage_configuration": self.coverage.coverage_configuration_identifier,
            "dataset_type": self.dataset_type,
            "aggregation_period": self.coverage.aggregation_period.value,
            "climatological_variable": self.coverage.climatic_indicator_name,
            "measure": self.coverage.measure_type.value,
            "year_period": self.coverage.year_period.value,
            "processing_method": self.processing_method.value,
            "processing_method_info": self.processing_method_info,
            "location": self.location.wkt,
        }
        if self.coverage.decade is not None:
            info["decade"] = self.coverage.decade
        if self.coverage.coverage_configuration_reference_period is not None:
            info[
                "reference_period"
            ] = self.coverage.coverage_configuration_reference_period.value
        return info
