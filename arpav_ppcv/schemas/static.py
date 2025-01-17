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
            self.ANOMALY: 0,
        }.get(self, 0)


class AggregationPeriod(str, enum.Enum):
    ANNUAL = "annual"
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
            self.THIRTY_YEAR: _("30yr"),
        }.get(self, self.value)

    def get_value_description(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.ANNUAL: _("annual description"),
            self.THIRTY_YEAR: _("30yr description"),
        }.get(self, self.value)

    def get_sort_order(self) -> int:
        return {
            self.ANNUAL: 0,
            self.THIRTY_YEAR: 0,
        }.get(self, 0)


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
