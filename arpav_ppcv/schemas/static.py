import enum
from typing import Final

import babel

from ..config import get_translations

NAME_PATTERN: Final[str] = r"^[a-z0-9_]+$"


class MeasureType(str, enum.Enum):
    ABSOLUTE = "ABSOLUTE"
    ANOMALY = "ANOMALY"

    def get_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.ABSOLUTE.name: _("absolute"),
            self.ANOMALY.name: _("anomaly"),
        }[self.name] or self.name

    def get_description(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.ABSOLUTE.name: _("absolute description"),
            self.ANOMALY.name: _("anomaly description"),
        }[self.name] or self.name

    def get_sort_order(self) -> int:
        return {
            self.ABSOLUTE.name: 0,
            self.ANOMALY.name: 0,
        }[self.name]


class AggregationPeriod(str, enum.Enum):
    ANNUAL = "ANNUAL"
    THIRTY_YEAR = "THIRTY_YEAR"

    def get_display_name(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.ANNUAL.name: _("annual"),
            self.THIRTY_YEAR.name: _("30yr"),
        }[self.name] or self.name

    def get_description(self, locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return {
            self.ANNUAL.name: _("annual description"),
            self.THIRTY_YEAR.name: _("30yr description"),
        }[self.name] or self.name

    def get_sort_order(self) -> int:
        return {
            self.ANNUAL.name: 0,
            self.THIRTY_YEAR.name: 0,
        }[self.name]
