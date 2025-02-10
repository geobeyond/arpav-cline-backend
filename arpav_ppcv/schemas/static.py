import enum
from typing import Final

import babel

from ..config import get_translations

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
    LOWER_UNCERTAINTY = "lower_uncertainty"
    UPPER_UNCERTAINTY = "upper_uncertainty"

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
            self.UPPER_UNCERTAINTY: _("upper uncertainty"),
        }.get(self, self.value)

    def get_value_description(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.MAIN: _("main description"),
            self.LOWER_UNCERTAINTY: _("lower uncertainty description"),
            self.UPPER_UNCERTAINTY: _("upper uncertainty description"),
        }.get(self, self.value)

    def get_sort_order(self) -> int:
        return {
            self.LOWER_UNCERTAINTY: 0,
            self.MAIN: 1,
            self.UPPER_UNCERTAINTY: 2,
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
            self.CLIMATE_STANDARD_NORMAL_1961_1990.name: _("1961-1990 description"),
            self.CLIMATE_STANDARD_NORMAL_1991_2020.name: _("1991-2020 description"),
        }.get(self, self.value)

    def get_internal_value(self) -> str:
        return self.value.replace("decade_", "").replace("_", "-")

    def get_sort_order(self) -> int:
        return {
            self.CLIMATE_STANDARD_NORMAL_1961_1990: 0,
            self.CLIMATE_STANDARD_NORMAL_1991_2020: 1,
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
        return self.value.replace(
            "climate_standard_normal_", "").replace("_", "-")

    def get_sort_order(self) -> int:
        return {
            self.CLIMATE_STANDARD_NORMAL_1961_1990: 0,
            self.CLIMATE_STANDARD_NORMAL_1991_2020: 1,
        }.get(self, 0)


class CoverageTimeSeriesProcessingMethod(str, enum.Enum):
    NO_PROCESSING = "no_processing"
    LOESS_SMOOTHING = "loess_smoothing"
    MOVING_AVERAGE_11_YEARS = "moving_average_11_years"

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
            self.NO_PROCESSING.name: _("no processing"),
            self.LOESS_SMOOTHING.name: _("LOESS"),
            self.MOVING_AVERAGE_11_YEARS.name: _("centered 11-year moving average"),
        }.get(self, self.value)

    def get_value_description(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.NO_PROCESSING.name: _("no processing description"),
            self.LOESS_SMOOTHING.name: _("LOESS description"),
            self.MOVING_AVERAGE_11_YEARS.name: _(
                "centered 11-year moving average description"
            ),
        }.get(self, self.value)

    def get_sort_order(self) -> int:
        return {
            self.NO_PROCESSING.name: 0,
            self.LOESS_SMOOTHING.name: 0,
            self.MOVING_AVERAGE_11_YEARS.name: 0,
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
            self.NO_PROCESSING.name: _("no processing"),
            self.MOVING_AVERAGE_5_YEARS.name: _("centered 5-year moving average"),
            self.MANN_KENDALL_TREND: _("Mann-Kendall trend"),
            self.DECADE_AGGREGATION.name: _("Decade aggregation"),
        }[self.name] or self.name

    def get_value_description(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.NO_PROCESSING.name: _("no processing description"),
            self.MOVING_AVERAGE_5_YEARS.name: _(
                "centered 5-year moving average description"
            ),
            self.MANN_KENDALL_TREND: _("Mann-Kendall trend description"),
            self.DECADE_AGGREGATION.name: _("Decade aggregation description"),
        }.get(self, self.value)

    def get_sort_order(self) -> int:
        return {
            self.NO_PROCESSING.name: 0,
            self.MOVING_AVERAGE_5_YEARS.name: 1,
            self.MANN_KENDALL_TREND.name: 2,
            self.DECADE_AGGREGATION.name: 3,
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
