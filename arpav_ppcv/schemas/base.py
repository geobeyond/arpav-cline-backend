import enum
import typing
import typing_extensions

import babel
import pydantic
import sqlmodel

from ..config import get_translations


class Translatable(typing.Protocol):
    def get_display_name(self, locale: babel.Locale) -> str:
        ...


class CoreConfParamName(enum.Enum):
    AGGREGATION_PERIOD = "aggregation_period"
    ARCHIVE = "archive"
    CLIMATOLOGICAL_MODEL = "climatological_model"
    CLIMATOLOGICAL_VARIABLE = "climatological_variable"
    HISTORICAL_VARIABLE = "historical_variable"
    HISTORICAL_YEAR_PERIOD = "historical_year_period"
    MEASURE = "measure"
    SCENARIO = "scenario"
    UNCERTAINTY_TYPE = "uncertainty_type"
    YEAR_PERIOD = "year_period"


class Season(enum.Enum):
    WINTER = "WINTER"
    SPRING = "SPRING"
    SUMMER = "SUMMER"
    AUTUMN = "AUTUMN"

    def get_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.WINTER.name: _("winter"),
            self.SPRING.name: _("spring"),
            self.SUMMER.name: _("summer"),
            self.AUTUMN.name: _("autumn"),
        }[self.name] or self.name


class ObservationDataSmoothingStrategy(enum.Enum):
    NO_SMOOTHING = "NO_SMOOTHING"
    MOVING_AVERAGE_5_YEARS = "MOVING_AVERAGE_5_YEARS"

    def get_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.NO_SMOOTHING.name: _("no processing"),
            self.MOVING_AVERAGE_5_YEARS.name: _("centered 5-year moving average"),
        }[self.name] or self.name


UNCERTAINTY_TIME_SERIES_PATTERN = "**UNCERTAINTY**"
RELATED_TIME_SERIES_PATTERN = "**RELATED**"


class ObservationAggregationType(str, enum.Enum):
    MONTHLY = "MONTHLY"
    SEASONAL = "SEASONAL"
    YEARLY = "YEARLY"

    def get_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.MONTHLY.name: _("monthly"),
            self.SEASONAL.name: _("seasonal"),
            self.YEARLY.name: _("yearly"),
        }[self.name] or self.name


class CoverageDataSmoothingStrategy(enum.Enum):
    NO_SMOOTHING = "NO_SMOOTHING"
    LOESS_SMOOTHING = "LOESS_SMOOTHING"
    MOVING_AVERAGE_11_YEARS = "MOVING_AVERAGE_11_YEARS"

    def get_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.NO_SMOOTHING.name: _("no processing"),
            self.LOESS_SMOOTHING.name: _("LOESS"),
            self.MOVING_AVERAGE_11_YEARS.name: _("centered 11-year moving average"),
        }[self.name] or self.name


class StaticCoverageSeriesParameter(enum.Enum):
    SERIES_NAME = "SERIES_NAME"
    PROCESSING_METHOD = "PROCESSING_METHOD"
    COVERAGE_IDENTIFIER = "COVERAGE_IDENTIFIER"
    COVERAGE_CONFIGURATION = "COVERAGE_CONFIGURATION"

    def get_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.SERIES_NAME.name: _("series name"),
            self.PROCESSING_METHOD.name: _("processing method"),
            self.COVERAGE_IDENTIFIER.name: _("coverage identifier"),
            self.COVERAGE_CONFIGURATION.name: _("coverage configuration"),
        }[self.name] or self.name


class StaticObservationSeriesParameter(enum.Enum):
    SERIES_NAME = "SERIES_NAME"
    PROCESSING_METHOD = "PROCESSING_METHOD"
    VARIABLE = "VARIABLE"
    STATION = "STATION"
    SERIES_ELABORATION = "SERIES_ELABORATION"
    DERIVED_SERIES = "DERIVED_SERIES"

    def get_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.SERIES_NAME.name: _("series name"),
            self.PROCESSING_METHOD.name: _("processing method"),
            self.VARIABLE.name: _("variable"),
            self.STATION.name: _("station"),
            self.SERIES_ELABORATION.name: _("series elaboration"),
            self.DERIVED_SERIES.name: _("derived series"),
        }[self.name] or self.name


class TimeSeriesElaboration(enum.Enum):
    ORIGINAL = "ORIGINAL"
    DERIVED = "DERIVED"

    def get_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.ORIGINAL.name: _("original"),
            self.DERIVED.name: _("derived"),
        }[self.name] or self.name


class ObservationDerivedSeries(enum.Enum):
    DECADE_SERIES = "DECADE_SERIES"
    MANN_KENDALL_SERIES = "MANN_KENDALL_SERIES"

    def get_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.DECADE_SERIES.name: _("decade series"),
            self.MANN_KENDALL_SERIES.name: _("Mann-Kendall series"),
        }[self.name] or self.name


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


class ResourceList(pydantic.BaseModel):
    items: list[sqlmodel.SQLModel]
