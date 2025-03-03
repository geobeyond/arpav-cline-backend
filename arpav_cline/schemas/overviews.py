"""Overview series are used to provide an overview of the whole area."""

import dataclasses
from typing import (
    Optional,
    TYPE_CHECKING,
)

import pydantic
import sqlalchemy
import sqlmodel

from . import static
from ..config import (
    get_translations,
    ThreddsServerSettings,
)
from ..thredds import crawler

if TYPE_CHECKING:
    import babel
    from . import climaticindicators


class BaseOverviewSeriesConfiguration(sqlmodel.SQLModel):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    netcdf_main_dataset_name: str
    thredds_url_pattern: str
    climatic_indicator_id: Optional[int] = sqlmodel.Field(
        default=None, foreign_key="climaticindicator.id"
    )


class ObservationOverviewSeriesConfiguration(
    BaseOverviewSeriesConfiguration, table=True
):
    climatic_indicator: "climaticindicators.ClimaticIndicator" = sqlmodel.Relationship(
        back_populates="observation_overview_series_configurations"
    )

    @pydantic.computed_field
    @property
    def identifier(self) -> str:
        return "overview-{data_category}-{climatic_indicator}".format(
            data_category=static.DataCategory.HISTORICAL.value,
            climatic_indicator=self.climatic_indicator.identifier,
        )

    @staticmethod
    def get_display_name(locale: "babel.Locale") -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("observation overview series configuration")

    @staticmethod
    def get_description(locale: "babel.Locale") -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("observation overview series configuration description")


class ObservationOverviewSeriesConfigurationCreate(sqlmodel.SQLModel):
    netcdf_main_dataset_name: str
    thredds_url_pattern: str
    climatic_indicator_id: int


class ObservationOverviewSeriesConfigurationUpdate(sqlmodel.SQLModel):
    netcdf_main_dataset_name: Optional[str] = None
    thredds_url_pattern: Optional[str] = None
    climatic_indicator_id: Optional[int] = None


class ForecastOverviewSeriesConfiguration(BaseOverviewSeriesConfiguration, table=True):
    lower_uncertainty_thredds_url_pattern: Optional[str] = None
    lower_uncertainty_netcdf_main_dataset_name: Optional[str] = None
    upper_uncertainty_thredds_url_pattern: Optional[str] = None
    upper_uncertainty_netcdf_main_dataset_name: Optional[str] = None
    scenarios: list[static.ForecastScenario] = sqlmodel.Field(
        default=list,
        sa_column=sqlalchemy.Column(
            sqlmodel.ARRAY(sqlmodel.Enum(static.ForecastScenario))
        ),
    )

    climatic_indicator: "climaticindicators.ClimaticIndicator" = sqlmodel.Relationship(
        back_populates="forecast_overview_series_configurations"
    )

    @pydantic.computed_field
    @property
    def identifier(self) -> str:
        return "overview-{data_category}-{climatic_indicator}".format(
            data_category=static.DataCategory.FORECAST.value,
            climatic_indicator=self.climatic_indicator.identifier,
        )

    @staticmethod
    def get_display_name(locale: "babel.Locale") -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("forecast overview series configuration")

    @staticmethod
    def get_description(locale: "babel.Locale") -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("forecast overview series configuration description")


class ForecastOverviewSeriesConfigurationCreate(sqlmodel.SQLModel):
    netcdf_main_dataset_name: str
    thredds_url_pattern: str
    climatic_indicator_id: int
    lower_uncertainty_thredds_url_pattern: Optional[str] = None
    lower_uncertainty_netcdf_main_dataset_name: Optional[str] = None
    upper_uncertainty_thredds_url_pattern: Optional[str] = None
    upper_uncertainty_netcdf_main_dataset_name: Optional[str] = None
    scenarios: Optional[list[static.ForecastScenario]] = None


class ForecastOverviewSeriesConfigurationUpdate(sqlmodel.SQLModel):
    netcdf_main_dataset_name: Optional[str] = None
    thredds_url_pattern: Optional[str] = None
    climatic_indicator_id: Optional[int] = None
    lower_uncertainty_thredds_url_pattern: Optional[str] = None
    lower_uncertainty_netcdf_main_dataset_name: Optional[str] = None
    upper_uncertainty_thredds_url_pattern: Optional[str] = None
    upper_uncertainty_netcdf_main_dataset_name: Optional[str] = None
    scenarios: Optional[list[static.ForecastScenario]] = None


@dataclasses.dataclass(frozen=True)
class ForecastOverviewSeriesInternal:
    configuration: ForecastOverviewSeriesConfiguration
    scenario: Optional[static.ForecastScenario] = None

    @property
    def identifier(self) -> str:
        pattern_parts = [self.configuration.identifier]
        pattern_parts.append(self.scenario.value if self.scenario else "*")
        return "-".join(pattern_parts)

    @property
    def lower_uncertainty_identifier(self) -> Optional[str]:
        result = None
        if self.configuration.lower_uncertainty_thredds_url_pattern:
            result = "-".join((self.identifier, "lower_uncertainty"))
        return result

    @property
    def upper_uncertainty_identifier(self) -> Optional[str]:
        result = None
        if self.configuration.upper_uncertainty_thredds_url_pattern:
            result = "-".join((self.identifier, "upper_uncertainty"))
        return result

    def get_netcdf_main_dataset_name(self) -> str:
        return self._render_templated_value(self.configuration.netcdf_main_dataset_name)

    def get_netcdf_lower_uncertainty_main_dataset_name(self) -> str:
        if (
            pattern := self.configuration.lower_uncertainty_netcdf_main_dataset_name
        ) is not None:
            result = self._render_templated_value(pattern)
        else:
            result = None
        return result

    def get_netcdf_upper_uncertainty_main_dataset_name(self) -> str:
        if (
            pattern := self.configuration.upper_uncertainty_netcdf_main_dataset_name
        ) is not None:
            result = self._render_templated_value(pattern)
        else:
            result = None
        return result

    def get_thredds_opendap_url(self, settings: ThreddsServerSettings) -> Optional[str]:
        return crawler.get_opendap_url(self._get_thredds_url_fragment(), settings)

    def get_lower_uncertainty_thredds_opendap_url(
        self, settings: ThreddsServerSettings
    ) -> Optional[str]:
        return crawler.get_opendap_url(
            self._get_lower_uncertainty_thredds_url_fragment(), settings
        )

    def get_upper_uncertainty_thredds_opendap_url(
        self, settings: ThreddsServerSettings
    ) -> Optional[str]:
        return crawler.get_opendap_url(
            self._get_upper_uncertainty_thredds_url_fragment(), settings
        )

    def _get_thredds_url_fragment(self) -> str:
        return self._render_templated_value(self.configuration.thredds_url_pattern)

    def _get_lower_uncertainty_thredds_url_fragment(self) -> Optional[str]:
        if (
            pattern := self.configuration.lower_uncertainty_thredds_url_pattern
        ) is not None:
            result = self._render_templated_value(pattern)
        else:
            result = None
        return result

    def _get_upper_uncertainty_thredds_url_fragment(self) -> Optional[str]:
        if (
            pattern := self.configuration.upper_uncertainty_thredds_url_pattern
        ) is not None:
            result = self._render_templated_value(pattern)
        else:
            result = None
        return result

    def _render_templated_value(self, value: str) -> str:
        return value.format(
            climatic_indicator=self.configuration.climatic_indicator.name,
            data_category=static.DataCategory.FORECAST.value,
            scenario=self.scenario.get_internal_value() if self.scenario else "",
        )


@dataclasses.dataclass(frozen=True)
class ObservationOverviewSeriesInternal:
    configuration: ObservationOverviewSeriesConfiguration

    @property
    def identifier(self) -> str:
        return "-".join((self.configuration.identifier, "series"))

    def get_netcdf_main_dataset_name(self) -> str:
        return self._render_templated_value(self.configuration.netcdf_main_dataset_name)

    def get_thredds_opendap_url(self, settings: ThreddsServerSettings) -> Optional[str]:
        return crawler.get_opendap_url(self._get_thredds_url_fragment(), settings)

    def _get_thredds_url_fragment(self) -> str:
        return self._render_templated_value(self.configuration.thredds_url_pattern)

    def _render_templated_value(self, value: str) -> str:
        return value.format(
            climatic_indicator=self.configuration.climatic_indicator.name,
            data_category=static.DataCategory.FORECAST.value,
        )
