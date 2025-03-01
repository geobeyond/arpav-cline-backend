import enum
import typing
from typing import TYPE_CHECKING

import typing_extensions

import babel
import geoalchemy2
import geojson_pydantic
import pydantic
import sqlalchemy
import sqlmodel

from ..config import get_translations

from . import fields

if TYPE_CHECKING:
    from . import coverages


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


class SpatialRegion(sqlmodel.SQLModel, table=True):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    name: str = sqlmodel.Field(nullable=False, unique=True)
    internal_value: str
    display_name_english: str = sqlmodel.Field(default="")
    display_name_italian: str = sqlmodel.Field(default="")
    sort_order: int = sqlmodel.Field(default=0)
    geom: fields.WkbElement = sqlmodel.Field(
        sa_column=sqlalchemy.Column(
            geoalchemy2.Geometry(
                srid=4326,
                geometry_type="MULTIPOLYGON",
                spatial_index=True,
            )
        )
    )

    forecast_coverage_configurations: list[
        "coverages.ForecastCoverageConfiguration"
    ] = sqlmodel.Relationship(back_populates="spatial_region")
    historical_coverage_configurations: list[
        "coverages.HistoricalCoverageConfiguration"
    ] = sqlmodel.Relationship(back_populates="spatial_region")


class SpatialRegionCreate(sqlmodel.SQLModel):
    name: str
    internal_value: str
    display_name_english: str = ""
    display_name_italian: str = ""
    sort_order: int = 0
    geom: geojson_pydantic.MultiPolygon


class SpatialRegionUpdate(sqlmodel.SQLModel):
    name: str | None = None
    internal_value: str | None = None
    display_name_english: str | None = None
    display_name_italian: str | None = None
    sort_order: int | None = None
    geom: geojson_pydantic.MultiPolygon | None = None


class ResourceList(pydantic.BaseModel):
    items: list[sqlmodel.SQLModel]
