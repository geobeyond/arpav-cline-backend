import datetime as dt
import dataclasses
from typing import (
    Optional,
    TYPE_CHECKING,
)

import geohashr
import pandas as pd
import shapely

if TYPE_CHECKING:
    from .coverages import ForecastCoverageInternal
    from .observations import (
        ObservationSeriesConfiguration,
        ObservationStation,
    )
    from .base import (
        CoverageDataSmoothingStrategy,
        ObservationDataSmoothingStrategy,
    )
    from .static import ForecastDatasetType


@dataclasses.dataclass
class ForecastDataSeries:
    forecast_coverage: "ForecastCoverageInternal"
    dataset_type: "ForecastDatasetType"
    smoothing_strategy: "CoverageDataSmoothingStrategy"
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
                self.smoothing_strategy.value.lower(),
            )
        )


@dataclasses.dataclass
class ObservationStationDataSeries:
    observation_series_configuration: "ObservationSeriesConfiguration"
    observation_station: "ObservationStation"
    smoothing_strategy: "ObservationDataSmoothingStrategy"
    data_: Optional[pd.Series] = None

    @property
    def identifier(self) -> str:
        return "-".join(
            (
                self.observation_series_configuration.identifier,
                self.observation_station.code,
                self.smoothing_strategy.value.lower(),
            )
        )
