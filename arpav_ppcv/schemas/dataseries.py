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
import shapely

from ..config import get_translations
from . import static

if TYPE_CHECKING:
    import babel
    from .coverages import (
        ForecastCoverageInternal,
        HistoricalCoverageInternal,
    )
    from .observations import (
        ObservationSeriesConfiguration,
        ObservationStation,
    )
    from .overviews import (
        ForecastOverviewSeriesInternal,
        ObservationOverviewSeriesInternal,
    )


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
    overview_series: "ObservationOverviewSeriesInternal"
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
    overview_series: "ForecastOverviewSeriesInternal"
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
    forecast_coverage: "ForecastCoverageInternal"
    dataset_type: static.DatasetType
    processing_method: static.CoverageTimeSeriesProcessingMethod
    temporal_start: Optional[dt.date]
    temporal_end: Optional[dt.date]
    location: shapely.Point
    data_: Optional[pd.Series] = None

    @property
    def identifier(self) -> str:
        return "-".join(
            (
                self.forecast_coverage.identifier,
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


@dataclasses.dataclass
class ObservationStationDataSeries:
    observation_series_configuration: "ObservationSeriesConfiguration"
    observation_station: "ObservationStation"
    processing_method: static.ObservationTimeSeriesProcessingMethod
    data_: Optional[pd.Series] = None

    @property
    def identifier(self) -> str:
        return "-".join(
            (
                self.observation_series_configuration.identifier,
                self.observation_station.code,
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


@dataclasses.dataclass
class HistoricalDataSeries:
    historical_coverage: "HistoricalCoverageInternal"
    dataset_type: static.DatasetType
    processing_method: static.CoverageTimeSeriesProcessingMethod
    temporal_start: Optional[dt.date]
    temporal_end: Optional[dt.date]
    location: shapely.Point
    data_: Optional[pd.Series] = None

    @property
    def identifier(self) -> str:
        return "-".join(
            (
                self.historical_coverage.identifier,
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
        return _("historical data series")

    @staticmethod
    def get_description(locale: "babel.Locale") -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("historical data series description")
