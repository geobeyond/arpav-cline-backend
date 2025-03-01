import enum
import typing
from typing import Optional

from ..config import get_translations

from . import static

if typing.TYPE_CHECKING:
    import babel

    from .climaticindicators import ClimaticIndicator


def parse_legacy_aggregation_period(
    legacy_value: str,
) -> Optional[static.AggregationPeriod]:
    parsed = {
        "30yr": static.AggregationPeriod.THIRTY_YEAR,
    }.get(legacy_value)
    if parsed is not None:
        result = parsed
    else:
        result = static.AggregationPeriod(legacy_value)
    return result


def convert_to_aggregation_period(
    aggregation_period: static.AggregationPeriod,
) -> Optional[str]:
    return {
        aggregation_period.THIRTY_YEAR: "30yr",
        aggregation_period.ANNUAL: "annual",
    }.get(aggregation_period, aggregation_period.value)


def convert_to_uncertainty_type(dataset_type: static.DatasetType) -> Optional[str]:
    return {
        dataset_type.LOWER_UNCERTAINTY: "lower_bound",
        dataset_type.UPPER_UNCERTAINTY: "upper_bound",
    }.get(dataset_type, dataset_type.value)


def convert_overview_historical_variable(
    climatic_indicator: "ClimaticIndicator",
) -> str:
    return {
        "tas": "tdd",
    }.get(climatic_indicator.name, "")


class CoverageDataSmoothingStrategy(enum.Enum):
    NO_SMOOTHING = "NO_SMOOTHING"
    LOESS_SMOOTHING = "LOESS_SMOOTHING"
    MOVING_AVERAGE_11_YEARS = "MOVING_AVERAGE_11_YEARS"

    def get_display_name(self, locale: "babel.Locale") -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.NO_SMOOTHING.name: _("no processing"),
            self.LOESS_SMOOTHING.name: _("LOESS"),
            self.MOVING_AVERAGE_11_YEARS.name: _("centered 11-year moving average"),
        }[self.name] or self.name

    def to_processing_method(self):
        return {
            self.NO_SMOOTHING: static.CoverageTimeSeriesProcessingMethod.NO_PROCESSING,
            self.LOESS_SMOOTHING: static.CoverageTimeSeriesProcessingMethod.LOESS_SMOOTHING,
            self.MOVING_AVERAGE_11_YEARS: static.CoverageTimeSeriesProcessingMethod.MOVING_AVERAGE_11_YEARS,
        }[self]

    @classmethod
    def from_processing_method(
        cls, processing_method: static.CoverageTimeSeriesProcessingMethod
    ) -> "CoverageDataSmoothingStrategy":
        return {
            processing_method.NO_PROCESSING: cls.NO_SMOOTHING,
            processing_method.LOESS_SMOOTHING: cls.LOESS_SMOOTHING,
            processing_method.MOVING_AVERAGE_11_YEARS: cls.MOVING_AVERAGE_11_YEARS,
        }[processing_method]


class ObservationDataSmoothingStrategy(enum.Enum):
    NO_SMOOTHING = "NO_SMOOTHING"
    MOVING_AVERAGE_5_YEARS = "MOVING_AVERAGE_5_YEARS"

    def get_display_name(self, locale: "babel.Locale") -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.NO_SMOOTHING.name: _("no processing"),
            self.MOVING_AVERAGE_5_YEARS.name: _("centered 5-year moving average"),
        }[self.name] or self.name

    def to_processing_method(self):
        return {
            self.NO_SMOOTHING: static.CoverageTimeSeriesProcessingMethod.NO_PROCESSING,
            self.MOVING_AVERAGE_5_YEARS: static.ObservationTimeSeriesProcessingMethod.MOVING_AVERAGE_5_YEARS,
        }[self]

    @classmethod
    def from_processing_method(
        cls, processing_method: static.ObservationTimeSeriesProcessingMethod
    ) -> "ObservationDataSmoothingStrategy":
        return {
            processing_method.NO_PROCESSING: cls.NO_SMOOTHING,
            processing_method.MOVING_AVERAGE_5_YEARS: cls.MOVING_AVERAGE_5_YEARS,
        }[processing_method]
