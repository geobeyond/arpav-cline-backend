from typing import (
    Annotated,
    Final,
    Optional,
    TYPE_CHECKING,
)

import babel
import pydantic
import sqlmodel
from sqlalchemy.orm import relationship as sla_relationship

from . import static
from ..config import get_translations

if TYPE_CHECKING:
    from . import (
        coverages,
        overviews,
    )
    from .observations import (
        ClimaticIndicatorObservationName,
        ObservationMeasurement,
        ObservationSeriesConfiguration,
        ObservationStation,
    )

_name_description_text: Final[str] = (
    "Parameter name. Only alphanumeric characters and the underscore are allowed. "
    "Example: my_indicator"
)


class ClimaticIndicator(sqlmodel.SQLModel, table=True):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    name: str
    historical_coverages_internal_name: str | None
    measure_type: static.MeasureType
    aggregation_period: static.AggregationPeriod
    display_name_english: str = sqlmodel.Field(default="")
    display_name_italian: str = sqlmodel.Field(default="")
    description_english: str = sqlmodel.Field(default="")
    description_italian: str = sqlmodel.Field(default="")
    unit_english: str = sqlmodel.Field(default="")
    unit_italian: str = sqlmodel.Field(default="")
    palette: str
    color_scale_min: float
    color_scale_max: float
    data_precision: int = sqlmodel.Field(default=0)
    sort_order: int = sqlmodel.Field(default=0)

    observation_overview_series_configurations: list[
        "overviews.ObservationOverviewSeriesConfiguration"
    ] = sqlmodel.Relationship(back_populates="climatic_indicator")
    forecast_overview_series_configurations: list[
        "overviews.ForecastOverviewSeriesConfiguration"
    ] = sqlmodel.Relationship(back_populates="climatic_indicator")
    forecast_coverage_configurations: list[
        "coverages.ForecastCoverageConfiguration"
    ] = sqlmodel.Relationship(back_populates="climatic_indicator")
    historical_coverage_configurations: list[
        "coverages.HistoricalCoverageConfiguration"
    ] = sqlmodel.Relationship(back_populates="climatic_indicator")
    related_coverage_configurations: list[
        "coverages.CoverageConfiguration"
    ] = sqlmodel.Relationship(back_populates="climatic_indicator")

    observation_series_configurations: list[
        "ObservationSeriesConfiguration"
    ] = sqlmodel.Relationship(back_populates="climatic_indicator")

    observation_names: list["ClimaticIndicatorObservationName"] = sqlmodel.Relationship(
        back_populates="climatic_indicator",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )
    forecast_model_links: list[
        "coverages.ForecastModelClimaticIndicatorLink"
    ] = sqlmodel.Relationship(
        back_populates="climatic_indicator",
    )
    # this relationship is defined by using the fallback sqlalchemy relationship
    # method - this is in order to be able to specify the link table as a
    # string (a facility that sqlalchemy offers, but not sqlmodel) and avoid circular
    # dependencies which would otherwise occur if using sqlmodel's `link_model`
    # approach
    observation_stations: list["ObservationStation"] = sqlmodel.Relationship(
        sa_relationship=sla_relationship(
            secondary="observationstationclimaticindicatorlink",
            back_populates="climatic_indicators",
        )
    )

    measurements: list["ObservationMeasurement"] = sqlmodel.Relationship(
        back_populates="climatic_indicator",
        sa_relationship_kwargs={
            # ORM relationship config, which explicitly includes the
            # `delete` and `delete-orphan` options because we want the ORM
            # to try to delete monthly measurements when their related
            # climatic_indicator is deleted
            "cascade": "all, delete-orphan",
            # expect that the RDBMS handles cascading deletes
            "passive_deletes": True,
        },
    )

    @pydantic.computed_field
    @property
    def identifier(self) -> str:
        return "{name}-{measure_type}-{aggregation_period}".format(
            name=self.name,
            measure_type=self.measure_type.value.lower(),
            aggregation_period=self.aggregation_period.value.lower(),
        )

    def render_templated_value(self, template: str) -> str:
        rendered = template
        rendered = rendered.replace("{measure_type}", self.measure_type.value.lower())
        rendered = rendered.replace(
            "{aggregation_period}", self.aggregation_period.value.lower()
        )
        return rendered

    def __hash__(self):
        return hash(self.identifier)

    @staticmethod
    def get_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("climatic indicator")

    @staticmethod
    def get_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("climatic indicator description")


class ClimaticIndicatorObservationNameCreate(sqlmodel.SQLModel):
    observation_station_manager: static.ObservationStationManager
    indicator_observation_name: str


class ClimaticIndicatorObservationNameUpdate(sqlmodel.SQLModel):
    observation_station_manager: static.ObservationStationManager
    indicator_observation_name: str


class ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator(
    sqlmodel.SQLModel
):
    forecast_model_id: Optional[int] = sqlmodel.Field(
        # NOTE: foreign key already defined in __table_args__ in order to be able to
        # specify the ondelete behavior
        default=None,
        primary_key=True,
    )
    thredds_url_base_path: str
    thredds_url_uncertainties_base_path: Optional[str] = None


class ClimaticIndicatorForecastModelLinkUpdateEmbeddedInClimaticIndicator(
    sqlmodel.SQLModel
):
    forecast_model_id: Optional[int] = sqlmodel.Field(
        # NOTE: foreign key already defined in __table_args__ in order to be able to
        # specify the ondelete behavior
        default=None,
        primary_key=True,
    )
    thredds_url_base_path: str
    thredds_url_uncertainties_base_path: Optional[str] = None


class ClimaticIndicatorCreate(sqlmodel.SQLModel):
    name: Annotated[
        str,
        pydantic.Field(pattern=static.NAME_PATTERN, description=_name_description_text),
    ]
    historical_coverages_internal_name: Optional[str] = None
    measure_type: static.MeasureType
    aggregation_period: static.AggregationPeriod
    display_name_english: str = sqlmodel.Field(default="")
    display_name_italian: str = sqlmodel.Field(default="")
    description_english: str = sqlmodel.Field(default="")
    description_italian: str = sqlmodel.Field(default="")
    unit_english: str = sqlmodel.Field(default="")
    unit_italian: str = sqlmodel.Field(default="")
    palette: str
    color_scale_min: float = 0.0
    color_scale_max: float = 0.0
    data_precision: int = sqlmodel.Field(default=0)
    sort_order: int = sqlmodel.Field(default=0)
    observation_names: list["ClimaticIndicatorObservationNameCreate"] = sqlmodel.Field(
        default_factory=list
    )
    forecast_models: list[
        ClimaticIndicatorForecastModelLinkCreateEmbeddedInClimaticIndicator
    ] = sqlmodel.Field(default_factory=list)


class ClimaticIndicatorUpdate(sqlmodel.SQLModel):
    name: Annotated[
        Optional[str],
        pydantic.Field(pattern=static.NAME_PATTERN, description=_name_description_text),
    ] = None
    historical_coverages_internal_name: Optional[str] = None
    measure_type: Optional[static.MeasureType] = None
    aggregation_period: Optional[static.AggregationPeriod] = None
    display_name_english: Optional[str] = None
    display_name_italian: Optional[str] = None
    description_english: Optional[str] = None
    description_italian: Optional[str] = None
    unit_english: Optional[str] = None
    unit_italian: Optional[str] = None
    palette: Optional[str] = None
    color_scale_min: Optional[float] = None
    color_scale_max: Optional[float] = None
    data_precision: Optional[int] = None
    sort_order: Optional[int] = None
    observation_names: list["ClimaticIndicatorObservationNameUpdate"]
    forecast_models: Optional[
        list[ClimaticIndicatorForecastModelLinkUpdateEmbeddedInClimaticIndicator]
    ] = None
