import datetime as dt
import dataclasses
from typing import (
    Optional,
    TYPE_CHECKING,
)

import geohashr
import pandas as pd
import shapely

from ..config import get_translations
from . import static

if TYPE_CHECKING:
    import babel
    from .coverages import ForecastCoverageInternal
    from .observations import (
        ObservationSeriesConfiguration,
        ObservationStation,
    )


@dataclasses.dataclass
class ForecastDataSeries:
    forecast_coverage: "ForecastCoverageInternal"
    dataset_type: static.ForecastDatasetType
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
                self.processing_method.value.lower(),
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
                self.processing_method.value.lower(),
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
