import dataclasses
import enum
import logging
from typing import (
    Final,
    TYPE_CHECKING,
)

import babel

from ..config import (
    get_translations,
    LOCALE_EN,
    LOCALE_IT,
    ThreddsServerSettings,
)

if TYPE_CHECKING:
    from .coverages import (
        ForecastCoverageInternal,
        HistoricalCoverageInternal,
    )
    from .overviews import (
        ForecastOverviewSeriesInternal,
        ObservationOverviewSeriesInternal,
    )

logger = logging.getLogger(__name__)

NAME_PATTERN: Final[str] = r"^[a-z0-9_]+$"
FORECAST_MODEL_NAME_PATTERN: Final[str] = r"^[a-z0-9_]+$"


class ForecastScenario(str, enum.Enum):
    RCP26 = "rcp26"
    RCP45 = "rcp45"
    RCP85 = "rcp85"

    @staticmethod
    def get_param_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("forecast scenario")

    @staticmethod
    def get_param_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("forecast scenario description")

    def get_value_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.RCP26: _("rcp26"),
            self.RCP45: _("rcp45"),
            self.RCP85: _("rcp85"),
        }.get(self, self.value)

    def get_value_description(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.RCP26: _("rcp26 description"),
            self.RCP45: _("rcp45 description"),
            self.RCP85: _("rcp85 description"),
        }.get(self, self.value)

    def get_sort_order(self) -> int:
        return {
            self.RCP26: 0,
            self.RCP45: 0,
            self.RCP85: 0,
        }.get(self, 0)

    def get_internal_value(self):
        return {
            self.RCP26: "rcp26",
            self.RCP45: "rcp45",
            self.RCP85: "rcp85",
        }.get(self, self.value)


class DataCategory(str, enum.Enum):
    FORECAST = "forecast"
    HISTORICAL = "historical"

    @staticmethod
    def get_param_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("data category")

    @staticmethod
    def get_param_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("data category description")

    def get_value_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.FORECAST: _("forecast"),
            self.HISTORICAL: _("historical"),
        }.get(self, self.value)

    def get_value_description(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.FORECAST: _("forecast description"),
            self.HISTORICAL: _("historical description"),
        }.get(self, self.value)

    def get_sort_order(self) -> int:
        return {
            self.FORECAST: 0,
            self.HISTORICAL: 1,
        }.get(self, 0)


class MeasureType(str, enum.Enum):
    ABSOLUTE = "absolute"
    ANOMALY = "anomaly"

    @staticmethod
    def get_param_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("measure type")

    @staticmethod
    def get_param_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("measure type description")

    def get_value_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.ABSOLUTE: _("absolute"),
            self.ANOMALY: _("anomaly"),
        }.get(self, self.value)

    def get_value_description(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.ABSOLUTE: _("absolute description"),
            self.ANOMALY: _("anomaly description"),
        }.get(self, self.value)

    def get_sort_order(self) -> int:
        return {
            self.ABSOLUTE: 0,
            self.ANOMALY: 1,
        }.get(self, 0)


class AggregationPeriod(str, enum.Enum):
    ANNUAL = "annual"
    TEN_YEAR = "ten_year"
    THIRTY_YEAR = "thirty_year"

    @staticmethod
    def get_param_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("aggregation period")

    @staticmethod
    def get_param_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("aggregation period description")

    def get_value_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.ANNUAL: _("annual"),
            self.TEN_YEAR: _("10yr"),
            self.THIRTY_YEAR: _("30yr"),
        }.get(self, self.value)

    def get_value_description(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.ANNUAL: _("annual description"),
            self.TEN_YEAR: _("10yr description"),
            self.THIRTY_YEAR: _("30yr description"),
        }.get(self, self.value)

    def get_sort_order(self) -> int:
        return {
            self.ANNUAL: 0,
            self.TEN_YEAR: 2,
            self.THIRTY_YEAR: 1,
        }.get(self, 0)


class ObservationYearPeriod(str, enum.Enum):
    # This does not have any translations or internal value because it is only meant
    # for internal usage and is not intended for exposing outside the system
    ALL_YEAR = "all_year"
    WINTER = "winter"
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    JANUARY = "january"
    FEBRUARY = "february"
    MARCH = "march"
    APRIL = "april"
    MAY = "may"
    JUNE = "june"
    JULY = "july"
    AUGUST = "august"
    SEPTEMBER = "september"
    OCTOBER = "october"
    NOVEMBER = "november"
    DECEMBER = "december"

    def get_month_filter(self) -> list[int]:
        return {
            ObservationYearPeriod.ALL_YEAR: (7,),
            ObservationYearPeriod.WINTER: (1, 2, 12),
            ObservationYearPeriod.SPRING: (3, 4, 5),
            ObservationYearPeriod.SUMMER: (6, 7, 8),
            ObservationYearPeriod.AUTUMN: (9, 10, 11),
            ObservationYearPeriod.JANUARY: (1,),
            ObservationYearPeriod.FEBRUARY: (2,),
            ObservationYearPeriod.MARCH: (3,),
            ObservationYearPeriod.APRIL: (4,),
            ObservationYearPeriod.MAY: (5,),
            ObservationYearPeriod.JUNE: (6,),
            ObservationYearPeriod.JULY: (7,),
            ObservationYearPeriod.AUGUST: (8,),
            ObservationYearPeriod.SEPTEMBER: (9,),
            ObservationYearPeriod.OCTOBER: (10,),
            ObservationYearPeriod.NOVEMBER: (11,),
            ObservationYearPeriod.DECEMBER: (12,),
        }[self]


class HistoricalYearPeriod(str, enum.Enum):
    ALL_YEAR = "all_year"
    WINTER = "winter"
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    JANUARY = "january"
    FEBRUARY = "february"
    MARCH = "march"
    APRIL = "april"
    MAY = "may"
    JUNE = "june"
    JULY = "july"
    AUGUST = "august"
    SEPTEMBER = "september"
    OCTOBER = "october"
    NOVEMBER = "november"
    DECEMBER = "december"

    @staticmethod
    def get_param_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("year period")

    @staticmethod
    def get_param_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("year period description")

    def get_value_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.ALL_YEAR: _("all year"),
            self.WINTER: _("winter"),
            self.SPRING: _("spring"),
            self.SUMMER: _("summer"),
            self.AUTUMN: _("autumn"),
            self.JANUARY: _("january"),
            self.FEBRUARY: _("february"),
            self.MARCH: _("march"),
            self.APRIL: _("april"),
            self.MAY: _("may"),
            self.JUNE: _("june"),
            self.JULY: _("july"),
            self.AUGUST: _("august"),
            self.SEPTEMBER: _("september"),
            self.OCTOBER: _("october"),
            self.NOVEMBER: _("november"),
            self.DECEMBER: _("december"),
        }.get(self, self.value)

    def get_value_description(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.ALL_YEAR: _("all year description"),
            self.WINTER: _("winter description"),
            self.SPRING: _("spring description"),
            self.SUMMER: _("summer description"),
            self.AUTUMN: _("autumn description"),
            self.JANUARY: _("january description"),
            self.FEBRUARY: _("february description"),
            self.MARCH: _("march description"),
            self.APRIL: _("april description"),
            self.MAY: _("may description"),
            self.JUNE: _("june description"),
            self.JULY: _("july description"),
            self.AUGUST: _("august description"),
            self.SEPTEMBER: _("september description"),
            self.OCTOBER: _("october description"),
            self.NOVEMBER: _("november description"),
            self.DECEMBER: _("december description"),
        }.get(self, self.value)

    def get_sort_order(self) -> int:
        return {
            self.ALL_YEAR: 0,
            self.WINTER: 1,
            self.SPRING: 2,
            self.SUMMER: 3,
            self.AUTUMN: 4,
            self.JANUARY: 5,
            self.FEBRUARY: 6,
            self.MARCH: 7,
            self.APRIL: 8,
            self.MAY: 9,
            self.JUNE: 10,
            self.JULY: 11,
            self.AUGUST: 12,
            self.SEPTEMBER: 13,
            self.OCTOBER: 14,
            self.NOVEMBER: 15,
            self.DECEMBER: 16,
        }.get(self, 0)

    def get_internal_value(self) -> str:
        return {
            self.ALL_YEAR: "A00",
            self.WINTER: "S01",
            self.SPRING: "S02",
            self.SUMMER: "S03",
            self.AUTUMN: "S04",
            self.JANUARY: "M01",
            self.FEBRUARY: "M02",
            self.MARCH: "M03",
            self.APRIL: "M04",
            self.MAY: "M05",
            self.JUNE: "M06",
            self.JULY: "M07",
            self.AUGUST: "M08",
            self.SEPTEMBER: "M09",
            self.OCTOBER: "M10",
            self.NOVEMBER: "M11",
            self.DECEMBER: "M12",
        }.get(self, self.value)


class DatasetType(str, enum.Enum):
    MAIN = "main"
    LOWER_UNCERTAINTY = "forecast_lower_uncertainty"
    OBSERVATION = "observation"
    UPPER_UNCERTAINTY = "forecast_upper_uncertainty"

    @staticmethod
    def get_param_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("forecast dataset")

    @staticmethod
    def get_param_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("forecast dataset description")

    def get_value_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.MAIN: _("main"),
            self.LOWER_UNCERTAINTY: _("lower uncertainty"),
            self.OBSERVATION: _("observation measurement"),
            self.UPPER_UNCERTAINTY: _("upper uncertainty"),
        }.get(self, self.value)

    def get_value_description(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.MAIN: _("main description"),
            self.LOWER_UNCERTAINTY: _("lower uncertainty description"),
            self.OBSERVATION: _("observation measurement description"),
            self.UPPER_UNCERTAINTY: _("upper uncertainty description"),
        }.get(self, self.value)

    def get_sort_order(self) -> int:
        return {
            self.OBSERVATION: 0,
            self.LOWER_UNCERTAINTY: 1,
            self.MAIN: 2,
            self.UPPER_UNCERTAINTY: 3,
        }.get(self, 0)


class ForecastYearPeriod(str, enum.Enum):
    ALL_YEAR = "all_year"
    WINTER = "winter"
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"

    @staticmethod
    def get_param_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("year period")

    @staticmethod
    def get_param_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("year period description")

    def get_value_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.ALL_YEAR: _("all year"),
            self.WINTER: _("winter"),
            self.SPRING: _("spring"),
            self.SUMMER: _("summer"),
            self.AUTUMN: _("autumn"),
        }.get(self, self.value)

    def get_value_description(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.ALL_YEAR: _("all year description"),
            self.WINTER: _("winter description"),
            self.SPRING: _("spring description"),
            self.SUMMER: _("summer description"),
            self.AUTUMN: _("autumn description"),
        }.get(self, self.value)

    def get_sort_order(self) -> int:
        return {
            self.ALL_YEAR: 0,
            self.WINTER: 1,
            self.SPRING: 2,
            self.SUMMER: 3,
            self.AUTUMN: 4,
        }.get(self, 0)

    def get_internal_value(self) -> str:
        return {
            self.WINTER: "DJF",
            self.SPRING: "MAM",
            self.SUMMER: "JJA",
            self.AUTUMN: "SON",
        }.get(self, self.value)


class MeasurementAggregationType(str, enum.Enum):
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    YEARLY = "yearly"

    @staticmethod
    def get_param_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("measurement aggregation type")

    @staticmethod
    def get_param_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("measurement aggregation description")

    def get_value_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.MONTHLY: _("monthly"),
            self.SEASONAL: _("seasonal"),
            self.YEARLY: _("yearly"),
        }.get(self, self.value)

    def get_value_description(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.MONTHLY: _("monthly description"),
            self.SEASONAL: _("seasonal description"),
            self.YEARLY: _("yearly description"),
        }.get(self, self.value)

    def get_sort_order(self) -> int:
        return {
            self.MONTHLY: 0,
            self.SEASONAL: 0,
            self.YEARLY: 0,
        }.get(self, 0)


class HistoricalDecade(str, enum.Enum):
    DECADE_1961_1970 = "decade_1961_1970"
    DECADE_1971_1980 = "decade_1971_1980"
    DECADE_1981_1990 = "decade_1981_1990"
    DECADE_1991_2000 = "decade_1991_2000"
    DECADE_2001_2010 = "decade_2001_2010"
    DECADE_2011_2020 = "decade_2011_2020"
    DECADE_2021_2030 = "decade_2021_2030"
    DECADE_2031_2040 = "decade_2031_2040"

    @staticmethod
    def get_param_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("historical decade")

    @staticmethod
    def get_param_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("historical decade description")

    def get_value_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.DECADE_1961_1970: _("decade_1961_1970"),
            self.DECADE_1971_1980: _("decade_1971_1980"),
            self.DECADE_1981_1990: _("decade_1981_1990"),
            self.DECADE_1991_2000: _("decade_1991_2000"),
            self.DECADE_2001_2010: _("decade_2001_2010"),
            self.DECADE_2011_2020: _("decade_2011_2020"),
            self.DECADE_2021_2030: _("decade_2021_2030"),
            self.DECADE_2031_2040: _("decade_2031_2040"),
        }.get(self, self.value)

    def get_value_description(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.DECADE_1961_1970: _("decade_1961_1970 description"),
            self.DECADE_1971_1980: _("decade_1971_1980 description"),
            self.DECADE_1981_1990: _("decade_1981_1990 description"),
            self.DECADE_1991_2000: _("decade_1991_2000 description"),
            self.DECADE_2001_2010: _("decade_2001_2010 description"),
            self.DECADE_2011_2020: _("decade_2011_2020 description"),
            self.DECADE_2021_2030: _("decade_2021_2030 description"),
            self.DECADE_2031_2040: _("decade_2031_2040 description"),
        }.get(self, self.value)

    def get_internal_value(self) -> str:
        return self.value.replace("decade_", "").replace("_", "-")

    def get_sort_order(self) -> int:
        return {
            self.DECADE_1961_1970: 0,
            self.DECADE_1971_1980: 1,
            self.DECADE_1981_1990: 2,
            self.DECADE_1991_2000: 3,
            self.DECADE_2001_2010: 4,
            self.DECADE_2011_2020: 5,
            self.DECADE_2021_2030: 6,
            self.DECADE_2031_2040: 7,
        }.get(self, 0)


class HistoricalReferencePeriod(str, enum.Enum):
    CLIMATE_STANDARD_NORMAL_1961_1990 = "climate_standard_normal_1961_1990"
    CLIMATE_STANDARD_NORMAL_1991_2020 = "climate_standard_normal_1991_2020"

    @staticmethod
    def get_param_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("historical reference period")

    @staticmethod
    def get_param_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("historical reference period description")

    def get_value_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.CLIMATE_STANDARD_NORMAL_1961_1990: _("1961-1990"),
            self.CLIMATE_STANDARD_NORMAL_1991_2020: _("1991-2020"),
        }.get(self, self.value)

    def get_value_description(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.CLIMATE_STANDARD_NORMAL_1961_1990: _("1961-1990 description"),
            self.CLIMATE_STANDARD_NORMAL_1991_2020: _("1991-2020 description"),
        }.get(self, self.value)

    def get_internal_value(self) -> str:
        return self.value.replace("climate_standard_normal_", "").replace("_", "-")

    def get_sort_order(self) -> int:
        return {
            self.CLIMATE_STANDARD_NORMAL_1961_1990: 0,
            self.CLIMATE_STANDARD_NORMAL_1991_2020: 1,
        }.get(self, 0)


class CoverageTimeSeriesProcessingMethod(str, enum.Enum):
    NO_PROCESSING = "no_processing"
    LOESS_SMOOTHING = "loess_smoothing"
    MOVING_AVERAGE_11_YEARS = "moving_average_11_years"
    MANN_KENDALL_TREND = "mann_kendall_trend"
    DECADE_AGGREGATION = "decade_aggregation"

    @staticmethod
    def get_param_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("coverage data processing method")

    @staticmethod
    def get_param_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("coverage data processing method description")

    def get_value_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.NO_PROCESSING: _("no processing"),
            self.LOESS_SMOOTHING: _("LOESS"),
            self.MOVING_AVERAGE_11_YEARS: _("centered 11-year moving average"),
            self.MANN_KENDALL_TREND: _("Mann-Kendall trend"),
            self.DECADE_AGGREGATION: _("Decade aggregation"),
        }.get(self, self.value)

    def get_value_description(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.NO_PROCESSING: _("no processing description"),
            self.LOESS_SMOOTHING: _("LOESS description"),
            self.MOVING_AVERAGE_11_YEARS: _(
                "centered 11-year moving average description"
            ),
            self.MANN_KENDALL_TREND: _("Mann-Kendall trend description"),
            self.DECADE_AGGREGATION: _("Decade aggregation description"),
        }.get(self, self.value)

    def get_sort_order(self) -> int:
        return {
            self.NO_PROCESSING: 0,
            self.LOESS_SMOOTHING: 1,
            self.MOVING_AVERAGE_11_YEARS: 2,
            self.MANN_KENDALL_TREND: 3,
            self.DECADE_AGGREGATION: 4,
        }.get(self, 0)


class HistoricalTimeSeriesProcessingMethod(str, enum.Enum):
    DECADE_AGGREGATION = "decade_aggregation"
    LOESS_SMOOTHING = "loess_smoothing"
    MANN_KENDALL_TREND = "mann_kendall_trend"
    NO_PROCESSING = "no_processing"
    MOVING_AVERAGE_5_YEARS = "moving_average_5_years"

    @staticmethod
    def get_param_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("observation data processing method")

    @staticmethod
    def get_param_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("observation data processing method description")

    def get_value_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.DECADE_AGGREGATION: _("Decade aggregation"),
            self.LOESS_SMOOTHING: _("LOESS"),
            self.MANN_KENDALL_TREND: _("Mann-Kendall trend"),
            self.MOVING_AVERAGE_5_YEARS: _("centered 5-year moving average"),
            self.NO_PROCESSING: _("no processing"),
        }.get(self, self.value)

    def get_value_description(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.DECADE_AGGREGATION: _("Decade aggregation description"),
            self.LOESS_SMOOTHING: _("LOESS description"),
            self.MANN_KENDALL_TREND: _("Mann-Kendall trend description"),
            self.MOVING_AVERAGE_5_YEARS: _(
                "centered 5-year moving average description"
            ),
            self.NO_PROCESSING: _("no processing description"),
        }.get(self, self.value)

    def get_sort_order(self) -> int:
        return {
            self.DECADE_AGGREGATION: 3,
            self.LOESS_SMOOTHING: 1,
            self.MANN_KENDALL_TREND: 2,
            self.MOVING_AVERAGE_5_YEARS: 1,
            self.NO_PROCESSING: 0,
        }.get(self, 0)


class ObservationTimeSeriesProcessingMethod(str, enum.Enum):
    NO_PROCESSING = "no_processing"
    MOVING_AVERAGE_5_YEARS = "moving_average_5_years"
    MANN_KENDALL_TREND = "mann_kendall_trend"
    DECADE_AGGREGATION = "decade_aggregation"

    @staticmethod
    def get_param_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("observation data processing method")

    @staticmethod
    def get_param_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("observation data processing method description")

    def get_value_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.NO_PROCESSING: _("no processing"),
            self.MOVING_AVERAGE_5_YEARS: _("centered 5-year moving average"),
            self.MANN_KENDALL_TREND: _("Mann-Kendall trend"),
            self.DECADE_AGGREGATION: _("Decade aggregation"),
        }.get(self, self.value)

    def get_value_description(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.NO_PROCESSING: _("no processing description"),
            self.MOVING_AVERAGE_5_YEARS: _(
                "centered 5-year moving average description"
            ),
            self.MANN_KENDALL_TREND: _("Mann-Kendall trend description"),
            self.DECADE_AGGREGATION: _("Decade aggregation description"),
        }.get(self, self.value)

    def get_sort_order(self) -> int:
        return {
            self.NO_PROCESSING: 0,
            self.MOVING_AVERAGE_5_YEARS: 1,
            self.MANN_KENDALL_TREND: 2,
            self.DECADE_AGGREGATION: 3,
        }.get(self, 0)


class ObservationStationManager(str, enum.Enum):
    ARPAV = "arpa_v"
    ARPAFVG = "arpa_fvg"

    @staticmethod
    def get_param_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("observation station manager")

    @staticmethod
    def get_param_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("observation station manager description")

    def get_value_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.ARPAV: _("ARPAV"),
            self.ARPAFVG: _("ARPAFVG"),
        }.get(self, self.value)

    def get_value_description(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.ARPAV: _("ARPAV description"),
            self.ARPAFVG: _("ARPAFVG description"),
        }.get(self, self.value)

    def get_sort_order(self) -> int:
        return {
            self.ARPAV: 0,
            self.ARPAFVG: 0,
        }.get(self, 0)


@dataclasses.dataclass(frozen=True)
class StaticForecastCoverage:
    """This class provides static access to properties of a forecast coverage.

    It exists in order to allow THREDDS-related code paths to run without
    needing a DB connection.
    """

    aggregation_period: AggregationPeriod
    climatic_indicator_name: str
    climatic_indicator_name_translations: dict[babel.Locale, str]
    climatic_indicator_description_translations: dict[babel.Locale, str]
    color_scale_min: float
    color_scale_max: float
    coverage_configuration_identifier: str
    coverage_identifier: str
    forecast_model_name: str
    forecast_model_name_translations: dict[babel.Locale, str]
    lower_uncertainty_identifier: str | None
    lower_uncertainty_ncss_url: str | None
    lower_uncertainy_netcdf_variable_name: str | None
    measure_type: MeasureType
    netcdf_variable_name: str | None
    ncss_url: str | None
    palette: str
    scenario: ForecastScenario
    upper_uncertainty_identifier: str | None
    upper_uncertainty_ncss_url: str | None
    upper_uncertainy_netcdf_variable_name: str | None
    wms_base_url: str
    year_period: ForecastYearPeriod
    related_static_coverages: list["StaticForecastCoverage"] = dataclasses.field(
        default_factory=list
    )

    @classmethod
    def from_coverage(
        cls,
        cov: "ForecastCoverageInternal",
        settings: ThreddsServerSettings,
        related_covs: list["ForecastCoverageInternal"] | None = None,
    ) -> "StaticForecastCoverage":
        if (ncss_url := cov.get_thredds_ncss_url(settings)) is None:
            logger.warning("Could not find coverage's NCSS URL")
        if (netcdf_variable_name := cov.get_netcdf_main_dataset_name()) is None:
            logger.warning("Could not find coverage's NetCDF variable name")
        if (
            lower_uncert_nc_var := cov.get_netcdf_lower_uncertainty_main_dataset_name()
        ) is None:
            logger.info(
                f"Coverage {cov.identifier!r} does not specify a lower "
                f"uncertainty dataset"
            )
        if (
            upper_uncert_nc_var := cov.get_netcdf_upper_uncertainty_main_dataset_name()
        ) is None:
            logger.info(
                f"Coverage {cov.identifier!r} does not specify an upper "
                f"uncertainty dataset"
            )

        lower_uncert_ncss_url = None
        if (
            lower_uncert := getattr(cov, "lower_uncertainty_identifier", None)
        ) is not None:
            lower_uncert_ncss_url = cov.get_lower_uncertainty_thredds_ncss_url(settings)
        upper_uncert_ncss_url = None
        if (
            upper_uncert := getattr(cov, "upper_uncertainty_identifier", None)
        ) is not None:
            upper_uncert_ncss_url = cov.get_upper_uncertainty_thredds_ncss_url(settings)

        return cls(
            aggregation_period=cov.configuration.climatic_indicator.aggregation_period,
            climatic_indicator_name=cov.configuration.climatic_indicator.name,
            climatic_indicator_name_translations={
                LOCALE_EN: cov.configuration.climatic_indicator.display_name_english,
                LOCALE_IT: cov.configuration.climatic_indicator.display_name_italian,
            },
            climatic_indicator_description_translations={
                LOCALE_EN: cov.configuration.climatic_indicator.description_english,
                LOCALE_IT: cov.configuration.climatic_indicator.description_italian,
            },
            color_scale_min=cov.configuration.climatic_indicator.color_scale_min,
            color_scale_max=cov.configuration.climatic_indicator.color_scale_max,
            coverage_configuration_identifier=cov.configuration.identifier,
            coverage_identifier=cov.identifier,
            forecast_model_name=cov.forecast_model.name,
            forecast_model_name_translations={
                LOCALE_EN: cov.forecast_model.display_name_english,
                LOCALE_IT: cov.forecast_model.display_name_italian,
            },
            lower_uncertainty_identifier=lower_uncert,
            lower_uncertainty_ncss_url=lower_uncert_ncss_url,
            lower_uncertainy_netcdf_variable_name=lower_uncert_nc_var,
            measure_type=cov.configuration.climatic_indicator.measure_type,
            netcdf_variable_name=netcdf_variable_name,
            ncss_url=ncss_url,
            palette=cov.configuration.climatic_indicator.palette,
            scenario=cov.scenario,
            upper_uncertainty_identifier=upper_uncert,
            upper_uncertainty_ncss_url=upper_uncert_ncss_url,
            upper_uncertainy_netcdf_variable_name=upper_uncert_nc_var,
            wms_base_url=cov.get_wms_base_url(settings),
            year_period=cov.year_period,
            related_static_coverages=[
                StaticForecastCoverage.from_coverage(other_cov, settings)
                for other_cov in (related_covs or [])
            ],
        )


@dataclasses.dataclass(frozen=True)
class StaticHistoricalCoverage:
    """This class provides static access to properties of a historical coverage.

    It exists in order to allow THREDDS-related code paths to run without
    needing a DB connection.
    """

    aggregation_period: AggregationPeriod
    climatic_indicator_name: str
    climatic_indicator_name_translations: dict[babel.Locale, str]
    climatic_indicator_description_translations: dict[babel.Locale, str]
    color_scale_min: float
    color_scale_max: float
    coverage_configuration_identifier: str
    coverage_identifier: str
    measure_type: MeasureType
    netcdf_variable_name: str | None
    ncss_url: str | None
    palette: str
    wms_base_url: str
    year_period: HistoricalYearPeriod
    decade: HistoricalDecade | None = None
    coverage_configuration_reference_period: HistoricalReferencePeriod | None = None

    @classmethod
    def from_coverage(
        cls,
        cov: "HistoricalCoverageInternal",
        settings: ThreddsServerSettings,
    ) -> "StaticHistoricalCoverage":
        if (ncss_url := cov.get_thredds_ncss_url(settings)) is None:
            logger.warning("Could not find coverage's NCSS URL")
        if (netcdf_variable_name := cov.get_netcdf_main_dataset_name()) is None:
            logger.warning("Could not find coverage's NetCDF variable name")
        return cls(
            aggregation_period=cov.configuration.climatic_indicator.aggregation_period,
            climatic_indicator_name=cov.configuration.climatic_indicator.name,
            climatic_indicator_name_translations={
                LOCALE_EN: cov.configuration.climatic_indicator.display_name_english,
                LOCALE_IT: cov.configuration.climatic_indicator.display_name_italian,
            },
            climatic_indicator_description_translations={
                LOCALE_EN: cov.configuration.climatic_indicator.description_english,
                LOCALE_IT: cov.configuration.climatic_indicator.description_italian,
            },
            color_scale_min=cov.configuration.climatic_indicator.color_scale_min,
            color_scale_max=cov.configuration.climatic_indicator.color_scale_max,
            coverage_configuration_identifier=cov.configuration.identifier,
            coverage_configuration_reference_period=cov.configuration.reference_period,
            coverage_identifier=cov.identifier,
            decade=cov.decade,
            measure_type=cov.configuration.climatic_indicator.measure_type,
            netcdf_variable_name=netcdf_variable_name,
            ncss_url=ncss_url,
            palette=cov.configuration.climatic_indicator.palette,
            wms_base_url=cov.get_wms_base_url(settings),
            year_period=cov.year_period,
        )


@dataclasses.dataclass(frozen=True)
class StaticForecastOverviewSeries:
    """This class provides static access to properties of an overview forecast.

    It exists in order to allow THREDDS-related code paths to run without
    needing a DB connection.
    """

    coverage_configuration_identifier: str
    climatic_indicator_identifier: str
    climatic_indicator_name: str
    climatic_indicator_name_translations: dict[babel.Locale, str]
    file_download_url: str | None
    lower_uncertainty_file_download_url: str | None
    lower_uncertainty_identifier: str | None
    lower_uncertainy_netcdf_variable_name: str
    lower_uncertainty_opendap_url: str | None
    opendap_url: str | None
    netcdf_variable_name: str
    series_configuration_identifier: str
    upper_uncertainty_file_download_url: str | None
    upper_uncertainty_identifier: str | None
    upper_uncertainy_netcdf_variable_name: str
    upper_uncertainty_opendap_url: str | None
    scenario: ForecastScenario | None = None

    @property
    def identifier(self) -> str:
        pattern_parts = [self.series_configuration_identifier]
        pattern_parts.append(self.scenario.value if self.scenario else "*")
        return "-".join(pattern_parts)

    @classmethod
    def from_series(
        cls,
        series: "ForecastOverviewSeriesInternal",
        settings: ThreddsServerSettings,
    ):
        if (opendap_url := series.get_thredds_opendap_url(settings)) is None:
            logger.warning("Could not find overview series' OpenDAP URL")
        if (
            lower_opendap_url := series.get_lower_uncertainty_thredds_opendap_url(
                settings
            )
        ) is None:
            logger.warning(
                "Could not find overview series' lower uncertainty OpenDAP URL"
            )
        if (
            upper_opendap_url := series.get_upper_uncertainty_thredds_opendap_url(
                settings
            )
        ) is None:
            logger.warning(
                "Could not find overview series' upper uncertainty OpenDAP URL"
            )
        if (
            file_download_url := series.get_thredds_file_download_url(settings)
        ) is None:
            logger.warning("Could not find overview series' file download URL")
        if (
            lower_download_url
            := series.get_lower_uncertainty_thredds_file_download_url(settings)
        ) is None:
            logger.warning(
                "Could not find overview series' lower uncertainty file " "download URL"
            )
        if (
            upper_download_url
            := series.get_upper_uncertainty_thredds_file_download_url(settings)
        ) is None:
            logger.warning(
                "Could not find overview series' upper uncertainty file " "download URL"
            )
        return cls(
            coverage_configuration_identifier=series.configuration.identifier,
            climatic_indicator_identifier=series.configuration.climatic_indicator.identifier,
            climatic_indicator_name=series.configuration.climatic_indicator.name,
            climatic_indicator_name_translations={
                LOCALE_EN: series.configuration.climatic_indicator.display_name_english,
                LOCALE_IT: series.configuration.climatic_indicator.display_name_italian,
            },
            series_configuration_identifier=series.configuration.identifier,
            file_download_url=file_download_url,
            lower_uncertainty_file_download_url=lower_download_url,
            lower_uncertainty_identifier=series.lower_uncertainty_identifier,
            lower_uncertainy_netcdf_variable_name=(
                series.get_netcdf_lower_uncertainty_main_dataset_name()
            ),
            lower_uncertainty_opendap_url=lower_opendap_url,
            opendap_url=opendap_url,
            netcdf_variable_name=series.get_netcdf_main_dataset_name(),
            upper_uncertainty_file_download_url=upper_download_url,
            upper_uncertainty_identifier=series.upper_uncertainty_identifier,
            upper_uncertainy_netcdf_variable_name=(
                series.get_netcdf_upper_uncertainty_main_dataset_name()
            ),
            upper_uncertainty_opendap_url=upper_opendap_url,
            scenario=series.scenario,
        )


@dataclasses.dataclass(frozen=True)
class StaticHistoricalOverviewSeries:
    """This class provides static access to properties of an overview historical.

    It exists in order to allow THREDDS-related code paths to run without
    needing a DB connection.
    """

    aggregation_period: AggregationPeriod
    climatic_indicator_identifier: str
    climatic_indicator_name: str
    climatic_indicator_name_translations: dict[babel.Locale, str]
    coverage_configuration_identifier: str
    measure_type: MeasureType
    file_download_url: str | None
    opendap_url: str | None
    netcdf_variable_name: str
    series_configuration_identifier: str

    @property
    def identifier(self) -> str:
        return "-".join((self.series_configuration_identifier, "series"))

    @classmethod
    def from_series(
        cls,
        series: "ObservationOverviewSeriesInternal",
        settings: ThreddsServerSettings,
    ):
        if (opendap_url := series.get_thredds_opendap_url(settings)) is None:
            logger.warning("Could not find overview series' OpenDAP URL")
        if (
            file_download_url := series.get_thredds_file_download_url(settings)
        ) is None:
            logger.warning("Could not find overview series' file download URL")
        return cls(
            aggregation_period=series.configuration.climatic_indicator.aggregation_period,
            climatic_indicator_identifier=series.configuration.climatic_indicator.identifier,
            climatic_indicator_name=series.configuration.climatic_indicator.name,
            climatic_indicator_name_translations={
                LOCALE_EN: series.configuration.climatic_indicator.display_name_english,
                LOCALE_IT: series.configuration.climatic_indicator.display_name_italian,
            },
            coverage_configuration_identifier=series.configuration.identifier,
            measure_type=series.configuration.climatic_indicator.measure_type,
            file_download_url=file_download_url,
            opendap_url=opendap_url,
            netcdf_variable_name=series.get_netcdf_main_dataset_name(),
            series_configuration_identifier=series.configuration.identifier,
        )
