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
    from .base import CoverageDataSmoothingStrategy
    from .static import ForecastDatasetType


@dataclasses.dataclass
class ForecastDataSeries:
    forecast_coverage: "ForecastCoverageInternal"
    dataset_type: "ForecastDatasetType"
    smoothing_strategy: "CoverageDataSmoothingStrategy"
    temporal_start: Optional[dt.date]
    temporal_end: Optional[dt.date]
    location: shapely.Point

    @property
    def identifier(self) -> str:
        return "-".join(
            (
                self.forecast_coverage.identifier,
                self.dataset_type.value,
                geohashr.encode(self.location.x, self.location.y),
                self.smoothing_strategy.value.upper(),
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

    def get_data(self) -> Optional[pd.Series]:
        ...
