import dataclasses
import logging
import re
import uuid
from typing import (
    Annotated,
    Optional,
    Final,
    TYPE_CHECKING,
    TypedDict,
)

import babel
import pydantic
import sqlalchemy
import sqlmodel

from .. import exceptions
from ..config import (
    ThreddsServerSettings,
    get_translations,
)
from ..thredds import crawler
from . import (
    base,
    static,
)

if TYPE_CHECKING:
    from . import (
        base,
        climaticindicators,
        observations,
    )

logger = logging.getLogger(__name__)
_NAME_PATTERN: Final[str] = r"^[a-z0-9_]+$"

_name_description_text: Final[str] = (
    "Only alphanumeric characters and the underscore are allowed. "
    "Example: my_indicator"
)


class ForecastTimeWindow(sqlmodel.SQLModel, table=True):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    name: str = sqlmodel.Field(nullable=False, unique=True)
    internal_value: str
    display_name_english: str = sqlmodel.Field(default="")
    display_name_italian: str = sqlmodel.Field(default="")
    description_english: str = sqlmodel.Field(default="")
    description_italian: str = sqlmodel.Field(default="")
    sort_order: int = sqlmodel.Field(default=0)

    forecast_coverage_configuration_links: list[
        "ForecastCoverageConfigurationForecastTimeWindowLink"
    ] = sqlmodel.Relationship(back_populates="forecast_time_window")

    @staticmethod
    def get_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("time window")

    @staticmethod
    def get_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("time window description")

    def __hash__(self):
        return self.id


class ForecastTimeWindowCreate(sqlmodel.SQLModel):
    name: Annotated[
        str,
        pydantic.Field(pattern=static.NAME_PATTERN, description=_name_description_text),
    ]
    internal_value: str
    display_name_english: str = sqlmodel.Field(default="")
    display_name_italian: str = sqlmodel.Field(default="")
    description_english: str = sqlmodel.Field(default="")
    description_italian: str = sqlmodel.Field(default="")
    sort_order: int = sqlmodel.Field(default=0)


class ForecastTimeWindowUpdate(sqlmodel.SQLModel):
    name: str | None = None
    internal_value: str | None = None
    display_name_english: str | None = None
    display_name_italian: str | None = None
    description_english: str | None = None
    description_italian: str | None = None
    sort_order: int | None = None


class ForecastModel(sqlmodel.SQLModel, table=True):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    name: str = sqlmodel.Field(nullable=False, unique=True)
    internal_value: str
    display_name_english: str = sqlmodel.Field(default="")
    display_name_italian: str = sqlmodel.Field(default="")
    description_english: str = sqlmodel.Field(default="")
    description_italian: str = sqlmodel.Field(default="")
    sort_order: int = sqlmodel.Field(default=0)

    climatic_indicator_links: list[
        "ForecastModelClimaticIndicatorLink"
    ] = sqlmodel.Relationship(back_populates="forecast_model")
    # forecast_coverage_configuration_links: list[
    #     "ForecastCoverageConfigurationForecastModelLink"
    # ] = sqlmodel.Relationship(back_populates="forecast_model")
    forecast_model_group_links: list[
        "ForecastModelForecastModelGroupLink"
    ] = sqlmodel.Relationship(back_populates="forecast_model")

    @staticmethod
    def get_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("forecast model")

    @staticmethod
    def get_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("forecast model description")

    def __hash__(self):
        return self.id


class ForecastModelCreate(sqlmodel.SQLModel):
    name: Annotated[
        str,
        pydantic.Field(pattern=static.NAME_PATTERN, description=_name_description_text),
    ]
    internal_value: str
    display_name_english: str = sqlmodel.Field(default="")
    display_name_italian: str = sqlmodel.Field(default="")
    description_english: str = sqlmodel.Field(default="")
    description_italian: str = sqlmodel.Field(default="")
    sort_order: int = sqlmodel.Field(default=0)


class ForecastModelUpdate(sqlmodel.SQLModel):
    name: Annotated[
        str,
        pydantic.Field(pattern=static.NAME_PATTERN, description=_name_description_text),
    ] = None
    internal_value: str | None = None
    display_name_english: str | None = None
    display_name_italian: str | None = None
    description_english: str | None = None
    description_italian: str | None = None
    sort_order: int | None = None


class _BaseGroup(sqlmodel.SQLModel):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    name: str
    display_name_english: str = sqlmodel.Field(default="")
    display_name_italian: str = sqlmodel.Field(default="")
    description_english: str = sqlmodel.Field(default="")
    description_italian: str = sqlmodel.Field(default="")
    sort_order: int = sqlmodel.Field(default=0)


class _BaseGroupCreate(sqlmodel.SQLModel):
    name: str
    display_name_english: str = sqlmodel.Field(default="")
    display_name_italian: str = sqlmodel.Field(default="")
    description_english: str = sqlmodel.Field(default="")
    description_italian: str = sqlmodel.Field(default="")
    sort_order: int = sqlmodel.Field(default=0)


class _BaseGroupUpdate(sqlmodel.SQLModel):
    name: str | None = None
    display_name_english: str | None = None
    display_name_italian: str | None = None
    description_english: str | None = None
    description_italian: str | None = None
    sort_order: int | None = None


class ForecastModelGroup(_BaseGroup, table=True):
    forecast_coverage_configurations: list[
        "ForecastCoverageConfiguration"
    ] = sqlmodel.Relationship(back_populates="forecast_model_group")
    forecast_model_links: list[
        "ForecastModelForecastModelGroupLink"
    ] = sqlmodel.Relationship(back_populates="forecast_model_group")

    @staticmethod
    def get_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("forecast model group")

    @staticmethod
    def get_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("forecast model group description")


class ForecastModelGroupCreate(_BaseGroupCreate):
    forecast_models: list[int]


class ForecastModelGroupUpdate(_BaseGroupUpdate):
    forecast_models: list[int] | None = None


class ForecastModelForecastModelGroupLink(sqlmodel.SQLModel, table=True):
    __table_args__ = (
        sqlalchemy.ForeignKeyConstraint(
            [
                "forecast_model_id",
            ],
            [
                "forecastmodel.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete all possible values if the related forecast model gets deleted
        ),
        sqlalchemy.ForeignKeyConstraint(
            [
                "forecast_model_group_id",
            ],
            [
                "forecastmodelgroup.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete all possible values if the related forecast model group gets deleted
        ),
    )
    forecast_model_id: Optional[int] = sqlmodel.Field(
        # NOTE: foreign key already defined in __table_args__ in order to be able to
        # specify the ondelete behavior
        default=None,
        primary_key=True,
    )
    forecast_model_group_id: Optional[int] = sqlmodel.Field(
        # NOTE: foreign key already defined in __table_args__ in order to be able to
        # specify the ondelete behavior
        default=None,
        primary_key=True,
    )

    forecast_model: ForecastModel = sqlmodel.Relationship(
        back_populates="forecast_model_group_links"
    )
    forecast_model_group: ForecastModelGroup = sqlmodel.Relationship(
        back_populates="forecast_model_links"
    )


# class ForecastCoverageConfigurationForecastModelGroupLink(
#     sqlmodel.SQLModel, table=True
# ):
#     __table_args__ = (
#         sqlalchemy.ForeignKeyConstraint(
#             [
#                 "forecast_coverage_configuration_id",
#             ],
#             [
#                 "forecastcoverageconfiguration.id",
#             ],
#             onupdate="CASCADE",
#             ondelete="CASCADE",  # i.e. delete all possible values if the related coverage configuration gets deleted
#         ),
#         sqlalchemy.ForeignKeyConstraint(
#             [
#                 "forecast_model_group_id",
#             ],
#             [
#                 "forecastmodelgroup.id",
#             ],
#             onupdate="CASCADE",
#             ondelete="CASCADE",  # i.e. delete all possible values if the related forecast model group gets deleted
#         ),
#     )
#     forecast_coverage_configuration_id: Optional[int] = sqlmodel.Field(
#         # NOTE: foreign key already defined in __table_args__ in order to be able to
#         # specify the ondelete behavior
#         default=None,
#         primary_key=True,
#     )
#     forecast_model_group_id: Optional[int] = sqlmodel.Field(
#         # NOTE: foreign key already defined in __table_args__ in order to be able to
#         # specify the ondelete behavior
#         default=None,
#         primary_key=True,
#     )
#
#     forecast_coverage_configuration: "ForecastCoverageConfiguration" = (
#         sqlmodel.Relationship(back_populates="forecast_model_group_links")
#     )
#     forecast_model_group: ForecastModelGroup = sqlmodel.Relationship(
#         back_populates="forecast_coverage_configuration_links"
#     )


class ForecastYearPeriodGroup(_BaseGroup, table=True):
    # forecast_coverage_configuration_links: list[
    #     "ForecastCoverageConfigurationForecastYearPeriodGroupLink"
    # ] = sqlmodel.Relationship(back_populates="forecast_year_period_group")

    year_periods: list[static.ForecastYearPeriod] = sqlmodel.Field(
        default=list,
        sa_column=sqlalchemy.Column(
            sqlmodel.ARRAY(sqlmodel.Enum(static.ForecastYearPeriod))
        ),
    )

    forecast_coverage_configurations: list[
        "ForecastCoverageConfiguration"
    ] = sqlmodel.Relationship(back_populates="year_period_group")

    @staticmethod
    def get_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("forecast year period")

    @staticmethod
    def get_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("forecast year period description")


class ForecastYearPeriodGroupCreate(_BaseGroupCreate):
    year_periods: list[static.ForecastYearPeriod]


class ForecastYearPeriodGroupUpdate(_BaseGroupUpdate):
    year_periods: list[static.ForecastYearPeriod] | None = None


# class ForecastCoverageConfigurationForecastYearPeriodGroupLink(
#     sqlmodel.SQLModel, table=True
# ):
#     __table_args__ = (
#         sqlalchemy.ForeignKeyConstraint(
#             [
#                 "forecast_coverage_configuration_id",
#             ],
#             [
#                 "forecastcoverageconfiguration.id",
#             ],
#             onupdate="CASCADE",
#             ondelete="CASCADE",  # i.e. delete all possible values if the related coverage configuration gets deleted
#         ),
#         sqlalchemy.ForeignKeyConstraint(
#             [
#                 "forecast_year_period_group_id",
#             ],
#             [
#                 "forecastyearperiodgroup.id",
#             ],
#             onupdate="CASCADE",
#             ondelete="CASCADE",
#             # i.e. delete all possible values if the related forecast year period group gets deleted
#         ),
#     )
#     forecast_coverage_configuration_id: Optional[int] = sqlmodel.Field(
#         # NOTE: foreign key already defined in __table_args__ in order to be able to
#         # specify the ondelete behavior
#         default=None,
#         primary_key=True,
#     )
#     forecast_year_period_group_id: Optional[int] = sqlmodel.Field(
#         # NOTE: foreign key already defined in __table_args__ in order to be able to
#         # specify the ondelete behavior
#         default=None,
#         primary_key=True,
#     )
#
#     forecast_coverage_configuration: "ForecastCoverageConfiguration" = (
#         sqlmodel.Relationship(back_populates="forecast_year_period_group_links")
#     )
#     forecast_year_period_group: ForecastYearPeriodGroup = sqlmodel.Relationship(
#         back_populates="forecast_coverage_configuration_links"
#     )


class HistoricalYearPeriodGroup(_BaseGroup, table=True):
    # historical_coverage_configuration_links: list[
    #     "HistoricalCoverageConfigurationHistoricalYearPeriodGroupLink"
    # ] = sqlmodel.Relationship(back_populates="historical_year_period_group")

    year_periods: list[static.HistoricalYearPeriod] = sqlmodel.Field(
        default=list,
        sa_column=sqlalchemy.Column(
            sqlmodel.ARRAY(sqlmodel.Enum(static.HistoricalYearPeriod))
        ),
    )

    historical_coverage_configurations: list[
        "HistoricalCoverageConfiguration"
    ] = sqlmodel.Relationship(back_populates="year_period_group")

    @staticmethod
    def get_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("historical year period")

    @staticmethod
    def get_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("historical year period description")


class HistoricalYearPeriodGroupCreate(_BaseGroupCreate):
    year_periods: list[static.HistoricalYearPeriod]


class HistoricalYearPeriodGroupUpdate(_BaseGroupUpdate):
    year_periods: list[static.HistoricalYearPeriod] | None = None


# class HistoricalCoverageConfigurationHistoricalYearPeriodGroupLink(
#     sqlmodel.SQLModel, table=True
# ):
#     __table_args__ = (
#         sqlalchemy.ForeignKeyConstraint(
#             [
#                 "historical_coverage_configuration_id",
#             ],
#             [
#                 "historicalcoverageconfiguration.id",
#             ],
#             onupdate="CASCADE",
#             ondelete="CASCADE",  # i.e. delete all possible values if the related coverage configuration gets deleted
#         ),
#         sqlalchemy.ForeignKeyConstraint(
#             [
#                 "historical_year_period_group_id",
#             ],
#             [
#                 "historicalyearperiodgroup.id",
#             ],
#             onupdate="CASCADE",
#             ondelete="CASCADE",
#             # i.e. delete all possible values if the related historical year period group gets deleted
#         ),
#     )
#     historical_coverage_configuration_id: Optional[int] = sqlmodel.Field(
#         # NOTE: foreign key already defined in __table_args__ in order to be able to
#         # specify the ondelete behavior
#         default=None,
#         primary_key=True,
#     )
#     historical_year_period_group_id: Optional[int] = sqlmodel.Field(
#         # NOTE: foreign key already defined in __table_args__ in order to be able to
#         # specify the ondelete behavior
#         default=None,
#         primary_key=True,
#     )
#
#     historical_coverage_configuration: "HistoricalCoverageConfiguration" = (
#         sqlmodel.Relationship(back_populates="historical_year_period_group_links")
#     )
#     historical_year_period_group: HistoricalYearPeriodGroup = sqlmodel.Relationship(
#         back_populates="historical_coverage_configuration_links"
#     )


class ConfigurationParameterValue(sqlmodel.SQLModel, table=True):
    __table_args__ = (
        sqlalchemy.ForeignKeyConstraint(
            [
                "configuration_parameter_id",
            ],
            [
                "configurationparameter.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete param value if its related param gets deleted
        ),
    )
    id: uuid.UUID = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    internal_value: str
    display_name_english: Optional[str] = None
    display_name_italian: Optional[str] = None
    description_english: Optional[str] = None
    description_italian: Optional[str] = None
    sort_order: Optional[int] = 0
    configuration_parameter_id: uuid.UUID

    configuration_parameter: "ConfigurationParameter" = sqlmodel.Relationship(
        back_populates="allowed_values",
    )
    used_in_configurations: list[
        "ConfigurationParameterPossibleValue"
    ] = sqlmodel.Relationship(
        back_populates="configuration_parameter_value",
        sa_relationship_kwargs={
            "cascade": "all, delete, delete-orphan",
            "passive_deletes": True,
            "order_by": "ConfigurationParameterPossibleValue.configuration_parameter_value_id",
        },
    )


class ConfigurationParameterValueCreate(sqlmodel.SQLModel):
    internal_value: str
    name: Annotated[
        str,
        pydantic.Field(
            pattern=_NAME_PATTERN,
            help=(
                "Parameter value name. Only alphanumeric characters and the underscore "
                "are allowed. Example: my_param_value"
            ),
        ),
    ] = None
    configuration_parameter_id: uuid.UUID
    display_name_english: Optional[str] = None
    display_name_italian: Optional[str] = None
    description_english: Optional[str] = None
    description_italian: Optional[str] = None
    sort_order: Optional[int] = 0


class ConfigurationParameter(sqlmodel.SQLModel, table=True):
    id: uuid.UUID = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = sqlmodel.Field(unique=True, index=True)
    display_name_english: Optional[str] = None
    display_name_italian: Optional[str] = None
    description_english: Optional[str] = None
    description_italian: Optional[str] = None

    allowed_values: list[ConfigurationParameterValue] = sqlmodel.Relationship(
        back_populates="configuration_parameter",
        sa_relationship_kwargs={
            "cascade": "all, delete, delete-orphan",
            "passive_deletes": True,
            "order_by": "ConfigurationParameterValue.sort_order",
        },
    )


class ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
    sqlmodel.SQLModel
):
    internal_value: str
    name: Annotated[
        str,
        pydantic.Field(
            pattern=_NAME_PATTERN,
            help=(
                "Parameter value name. Only alphanumeric characters and the underscore "
                "are allowed. Example: my_param_value"
            ),
        ),
    ] = None
    display_name_english: Optional[str] = None
    display_name_italian: Optional[str] = None
    description_english: Optional[str] = None
    description_italian: Optional[str] = None
    sort_order: int


class ConfigurationParameterCreate(sqlmodel.SQLModel):
    name: Annotated[
        str,
        pydantic.Field(
            pattern=_NAME_PATTERN,
            help=(
                "Parameter name. Only alphanumeric characters and the underscore are "
                "allowed. Example: my_param"
            ),
        ),
    ]
    display_name_english: Optional[str] = None
    display_name_italian: Optional[str] = None
    description_english: Optional[str] = None
    description_italian: Optional[str] = None

    allowed_values: list[
        ConfigurationParameterValueCreateEmbeddedInConfigurationParameter
    ]


class ConfigurationParameterValueUpdateEmbeddedInConfigurationParameterEdit(
    sqlmodel.SQLModel
):
    id: Optional[uuid.UUID] = None
    internal_value: Optional[str] = None
    name: Annotated[Optional[str], pydantic.Field(pattern=_NAME_PATTERN)] = None
    display_name_english: Optional[str] = None
    display_name_italian: Optional[str] = None
    description_english: Optional[str] = None
    description_italian: Optional[str] = None
    sort_order: Optional[int] = None


class ConfigurationParameterUpdate(sqlmodel.SQLModel):
    name: Annotated[Optional[str], pydantic.Field(pattern=_NAME_PATTERN)] = None
    display_name_english: Optional[str] = None
    display_name_italian: Optional[str] = None
    description_english: Optional[str] = None
    description_italian: Optional[str] = None

    allowed_values: list[
        ConfigurationParameterValueUpdateEmbeddedInConfigurationParameterEdit
    ]


class CoverageConfiguration(sqlmodel.SQLModel, table=True):
    """Configuration for NetCDF datasets.

    Can refer to either model forecast data or historical data derived from
    observations.
    """

    id: uuid.UUID = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = sqlmodel.Field(unique=True, index=True)
    netcdf_main_dataset_name: str
    thredds_url_pattern: str
    wms_main_layer_name: Optional[str] = None
    wms_secondary_layer_name: Optional[str] = None
    climatic_indicator_id: Optional[int] = sqlmodel.Field(
        default=None, foreign_key="climaticindicator.id"
    )
    uncertainty_lower_bounds_coverage_configuration_id: Optional[
        uuid.UUID
    ] = sqlmodel.Field(default=None, foreign_key="coverageconfiguration.id")
    uncertainty_upper_bounds_coverage_configuration_id: Optional[
        uuid.UUID
    ] = sqlmodel.Field(default=None, foreign_key="coverageconfiguration.id")

    possible_values: list[
        "ConfigurationParameterPossibleValue"
    ] = sqlmodel.Relationship(
        back_populates="coverage_configuration",
        sa_relationship_kwargs={
            "cascade": "all, delete, delete-orphan",
            "passive_deletes": True,
        },
    )
    secondary_coverage_configurations: list[
        "RelatedCoverageConfiguration"
    ] = sqlmodel.Relationship(
        back_populates="main_coverage_configuration",
        sa_relationship_kwargs={
            "foreign_keys": (
                "RelatedCoverageConfiguration.main_coverage_configuration_id"
            ),
            "cascade": "all, delete, delete-orphan",
        },
    )
    primary_coverage_configurations: list[
        "RelatedCoverageConfiguration"
    ] = sqlmodel.Relationship(
        back_populates="secondary_coverage_configuration",
        sa_relationship_kwargs={
            "foreign_keys": (
                "RelatedCoverageConfiguration.secondary_coverage_configuration_id"
            ),
            "cascade": "all, delete, delete-orphan",
        },
    )
    climatic_indicator: "climaticindicators.ClimaticIndicator" = sqlmodel.Relationship(
        back_populates="related_coverage_configurations"
    )

    # related_observation_variable: "observations.Variable" = sqlmodel.Relationship(
    #     back_populates="related_coverage_configurations"
    # )

    uncertainty_lower_bounds_coverage_configuration: Optional[
        "CoverageConfiguration"
    ] = sqlmodel.Relationship(
        back_populates="is_lower_bounds_coverage_configuration_to",
        sa_relationship_kwargs={
            "foreign_keys": "CoverageConfiguration.uncertainty_lower_bounds_coverage_configuration_id",
            "remote_side": "CoverageConfiguration.id",
        },
    )
    is_lower_bounds_coverage_configuration_to: Optional[
        "CoverageConfiguration"
    ] = sqlmodel.Relationship(
        back_populates="uncertainty_lower_bounds_coverage_configuration",
        sa_relationship_kwargs={
            "foreign_keys": "CoverageConfiguration.uncertainty_lower_bounds_coverage_configuration_id",
        },
    )

    uncertainty_upper_bounds_coverage_configuration: Optional[
        "CoverageConfiguration"
    ] = sqlmodel.Relationship(
        back_populates="is_upper_bounds_coverage_configuration_to",
        sa_relationship_kwargs={
            "foreign_keys": "CoverageConfiguration.uncertainty_upper_bounds_coverage_configuration_id",
            "remote_side": "CoverageConfiguration.id",
        },
    )
    is_upper_bounds_coverage_configuration_to: Optional[
        "CoverageConfiguration"
    ] = sqlmodel.Relationship(
        back_populates="uncertainty_upper_bounds_coverage_configuration",
        sa_relationship_kwargs={
            "foreign_keys": "CoverageConfiguration.uncertainty_upper_bounds_coverage_configuration_id",
        },
    )

    @pydantic.computed_field()
    @property
    def coverage_id_pattern(self) -> str:
        other_parts = set()
        legacy_param_names = (
            "climatological_variable",
            "measure",
            "aggregation_period",
        )
        for pv in self.possible_values:
            param_name = pv.configuration_parameter_value.configuration_parameter.name
            if param_name not in legacy_param_names:
                other_parts.add(param_name)
        all_parts = ["name", "climatic_indicator"] + sorted(list(other_parts))
        return "-".join(f"{{{part}}}" for part in all_parts)

    @pydantic.computed_field()
    @property
    def archive(self) -> Optional[str]:
        result = None
        for pv in self.possible_values:
            if (
                pv.configuration_parameter_value.configuration_parameter.name
                == base.CoreConfParamName.ARCHIVE.value
            ):
                result = pv.configuration_parameter_value.name
                break
        return result

    def get_thredds_url_fragment(self, coverage_identifier: str) -> str:
        return self._render_templated_value(
            coverage_identifier, self.thredds_url_pattern
        )

    def get_main_netcdf_variable_name(self, coverage_identifier: str) -> str:
        return self._render_templated_value(
            coverage_identifier, self.netcdf_main_dataset_name
        )

    def get_wms_main_layer_name(self, coverage_identifier: str) -> str:
        return self._render_templated_value(
            coverage_identifier, self.wms_main_layer_name
        )

    def get_wms_secondary_layer_name(self, coverage_identifier: str) -> str:
        return self._render_templated_value(
            coverage_identifier, self.wms_secondary_layer_name
        )

    def _render_templated_value(self, coverage_identifier: str, template: str) -> str:
        try:
            used_values = self.retrieve_used_values(coverage_identifier)
        except IndexError as err:
            logger.exception("Could not retrieve used values")
            raise exceptions.InvalidCoverageIdentifierException() from err
        rendered = self.climatic_indicator.render_templated_value(template)
        for used_value in used_values:
            param_name = (
                used_value.configuration_parameter_value.configuration_parameter.name
            )
            param_internal_value = (
                used_value.configuration_parameter_value.internal_value
            )
            rendered = rendered.replace(f"{{{param_name}}}", param_internal_value)
        return rendered

    def build_coverage_identifier(
        self, parameters: list[ConfigurationParameterValue]
    ) -> str:
        id_parts = [self.name, self.climatic_indicator.identifier]
        for part in self.coverage_id_pattern.split("-")[2:]:
            param_name = part.translate(str.maketrans("", "", "{}"))
            for conf_param_value in parameters:
                conf_param = conf_param_value.configuration_parameter
                if conf_param.name == param_name:
                    id_parts.append(conf_param_value.name)
                    break
            else:
                raise ValueError(f"Could not find suitable value for {param_name!r}")
        return "-".join(id_parts)

    def retrieve_used_values(
        self, coverage_identifier: str
    ) -> list["ConfigurationParameterPossibleValue"]:
        parsed_parameters = self.retrieve_configuration_parameters(coverage_identifier)
        result = []
        for param_name, value in parsed_parameters.items():
            for pv in self.possible_values:
                matches_param_name = (
                    pv.configuration_parameter_value.configuration_parameter.name
                    == param_name
                )
                matches_param_value = pv.configuration_parameter_value.name == value
                if matches_param_name and matches_param_value:
                    result.append(pv)
                    break
            else:
                raise ValueError(f"Invalid parameter/value pair: {(param_name, value)}")
        return result

    def retrieve_configuration_parameters(
        self, coverage_identifier: str
    ) -> dict[str, str]:
        # - first in the coverage identifier is the cov_conf's `name`
        # - second is the cov conf's climatic_indicator `identifier`
        # - then we have all the conf params
        conf_param_name_parts = self.coverage_id_pattern.split("-")[2:]

        # - so, first is the cov_conf.name
        # - then the next three are the climatic_indicator identifier name parts
        # - finally, the conf param values
        conf_param_values = coverage_identifier.split("-")[4:]

        result = {}
        for index, param_part in enumerate(conf_param_name_parts):
            param_name = param_part.translate(str.maketrans("", "", "{}"))
            result[param_name] = conf_param_values[index]

        return result

    def get_seasonal_aggregation_query_filter(
        self, coverage_identifier: str
    ) -> Optional[base.Season]:
        used_values = self.retrieve_used_values(coverage_identifier)
        result = None
        for used_value in used_values:
            is_temporal_aggregation = (
                used_value.configuration_parameter_value.configuration_parameter.name
                in (
                    base.CoreConfParamName.YEAR_PERIOD.value,
                    base.CoreConfParamName.HISTORICAL_YEAR_PERIOD.value,
                )
            )
            if is_temporal_aggregation:
                value = used_value.configuration_parameter_value.name.lower()
                if value in ("winter",):
                    result = base.Season.WINTER
                elif value in ("spring",):
                    result = base.Season.SPRING
                elif value in ("summer",):
                    result = base.Season.SUMMER
                elif value in ("autumn",):
                    result = base.Season.AUTUMN
                break
        else:
            logger.warning(
                f"Could not determine appropriate season for coverage "
                f"identifier {coverage_identifier!r}"
            )
        return result


class CoverageConfigurationCreate(sqlmodel.SQLModel):
    name: Annotated[
        str,
        pydantic.Field(
            pattern=_NAME_PATTERN,
            help=(
                "Coverage configuration name. Only alphanumeric characters and the "
                "underscore are allowed. Example: my_name"
            ),
        ),
    ]
    netcdf_main_dataset_name: str
    # the point in having a wms_main_layer_name and wms_secondary_layer_name is to let
    # the frontend toggle between them
    wms_main_layer_name: Optional[str] = None
    wms_secondary_layer_name: Optional[str] = None
    thredds_url_pattern: str
    possible_values: list["ConfigurationParameterPossibleValueCreate"]
    climatic_indicator_id: int
    uncertainty_lower_bounds_coverage_configuration_id: Optional[uuid.UUID] = None
    uncertainty_upper_bounds_coverage_configuration_id: Optional[uuid.UUID] = None
    secondary_coverage_configurations_ids: Annotated[
        Optional[list[uuid.UUID]], pydantic.Field(default_factory=list)
    ]

    @pydantic.field_validator("thredds_url_pattern")
    @classmethod
    def validate_thredds_url_pattern(cls, v: str) -> str:
        for match_obj in re.finditer(r"(\{.*?\})", v):
            if re.match(_NAME_PATTERN, match_obj.group(1)[1:-1]) is None:
                raise ValueError(f"configuration parameter {v!r} has invalid name")
        return v.strip()


class CoverageConfigurationUpdate(sqlmodel.SQLModel):
    name: Annotated[Optional[str], pydantic.Field(pattern=_NAME_PATTERN)] = None
    netcdf_main_dataset_name: Optional[str] = None
    wms_main_layer_name: Optional[str] = None
    wms_secondary_layer_name: Optional[str] = None
    thredds_url_pattern: Optional[str] = None
    climatic_indicator_id: Optional[int] = None
    possible_values: list["ConfigurationParameterPossibleValueUpdate"]
    uncertainty_lower_bounds_coverage_configuration_id: Optional[uuid.UUID] = None
    uncertainty_upper_bounds_coverage_configuration_id: Optional[uuid.UUID] = None
    secondary_coverage_configurations_ids: Optional[list[uuid.UUID]] = None

    @pydantic.field_validator("thredds_url_pattern")
    @classmethod
    def validate_thredds_url_pattern(cls, v: str) -> str:
        for match_obj in re.finditer(r"(\{.*?\})", v):
            if re.match(_NAME_PATTERN, match_obj.group(1)[1:-1]) is None:
                raise ValueError(f"configuration parameter {v!r} has invalid name")
        return v.strip()


class RelatedCoverageConfiguration(sqlmodel.SQLModel, table=True):
    """Relates coverage configurations with each other.

    This model mediates an association table that governs a many-to-many relationship
    between a main coverage configuration and other coverage configurations.
    """

    main_coverage_configuration_id: Optional[uuid.UUID] = sqlmodel.Field(
        default=None, primary_key=True, foreign_key="coverageconfiguration.id"
    )
    secondary_coverage_configuration_id: Optional[uuid.UUID] = sqlmodel.Field(
        default=None,
        primary_key=True,
        foreign_key="coverageconfiguration.id",
    )

    main_coverage_configuration: CoverageConfiguration = sqlmodel.Relationship(
        back_populates="secondary_coverage_configurations",
        sa_relationship_kwargs={
            "foreign_keys": "RelatedCoverageConfiguration.main_coverage_configuration_id",
        },
    )
    secondary_coverage_configuration: CoverageConfiguration = sqlmodel.Relationship(
        back_populates="primary_coverage_configurations",
        sa_relationship_kwargs={
            "foreign_keys": "RelatedCoverageConfiguration.secondary_coverage_configuration_id",
        },
    )


class ConfigurationParameterPossibleValue(sqlmodel.SQLModel, table=True):
    """Possible values for a parameter of a coverage configuration.

    This model mediates an association table that governs a many-to-many relationship
    between a coverage configuration and a configuration parameter value."""

    __table_args__ = (
        sqlalchemy.ForeignKeyConstraint(
            [
                "coverage_configuration_id",
            ],
            [
                "coverageconfiguration.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete all possible values if the related coverage configuration gets deleted
        ),
        sqlalchemy.ForeignKeyConstraint(
            [
                "configuration_parameter_value_id",
            ],
            [
                "configurationparametervalue.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete all possible values if the related conf parameter value gets deleted
        ),
    )

    coverage_configuration_id: Optional[uuid.UUID] = sqlmodel.Field(
        # NOTE: foreign key already defined in __table_args__ in order to be able to
        # specify the ondelete behavior
        default=None,
        primary_key=True,
    )
    configuration_parameter_value_id: Optional[uuid.UUID] = sqlmodel.Field(
        # NOTE: foreign key already defined in __table_args__ in order to be able to
        # specify the ondelete behavior
        default=None,
        primary_key=True,
    )

    coverage_configuration: CoverageConfiguration = sqlmodel.Relationship(
        back_populates="possible_values"
    )
    configuration_parameter_value: ConfigurationParameterValue = sqlmodel.Relationship(
        back_populates="used_in_configurations"
    )


class ConfigurationParameterPossibleValueCreate(sqlmodel.SQLModel):
    configuration_parameter_value_id: uuid.UUID


class ConfigurationParameterPossibleValueUpdate(sqlmodel.SQLModel):
    configuration_parameter_value_id: uuid.UUID


@dataclasses.dataclass(frozen=True)
class CoverageInternal:
    configuration: CoverageConfiguration
    identifier: str

    def __hash__(self):
        return hash(self.identifier)


class VariableMenuTreeCombination(TypedDict):
    configuration_parameter: ConfigurationParameter
    values: list[ConfigurationParameterValue]


class HistoricalVariableMenuTree(TypedDict):
    historical_variable: ConfigurationParameterValue
    aggregation_period: ConfigurationParameterValue
    combinations: dict[str, VariableMenuTreeCombination]


class ForecastModelClimaticIndicatorLink(sqlmodel.SQLModel, table=True):
    __table_args__ = (
        sqlalchemy.ForeignKeyConstraint(
            [
                "forecast_model_id",
            ],
            [
                "forecastmodel.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete all possible values if the related forecast model gets deleted
        ),
        sqlalchemy.ForeignKeyConstraint(
            [
                "climatic_indicator_id",
            ],
            [
                "climaticindicator.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete all possible values if the related climatic indicator gets deleted
        ),
    )
    forecast_model_id: Optional[int] = sqlmodel.Field(
        # NOTE: foreign key already defined in __table_args__ in order to be able to
        # specify the ondelete behavior
        default=None,
        primary_key=True,
    )
    climatic_indicator_id: Optional[int] = sqlmodel.Field(
        # NOTE: foreign key already defined in __table_args__ in order to be able to
        # specify the ondelete behavior
        default=None,
        primary_key=True,
    )
    thredds_url_base_path: str
    thredds_url_uncertainties_base_path: Optional[str]

    forecast_model: "ForecastModel" = sqlmodel.Relationship(
        back_populates="climatic_indicator_links"
    )
    climatic_indicator: "climaticindicators.ClimaticIndicator" = sqlmodel.Relationship(
        back_populates="forecast_model_links"
    )


#
#
# class ForecastCoverageConfigurationForecastModelLink(sqlmodel.SQLModel, table=True):
#     __table_args__ = (
#         sqlalchemy.ForeignKeyConstraint(
#             [
#                 "forecast_coverage_configuration_id",
#             ],
#             [
#                 "forecastcoverageconfiguration.id",
#             ],
#             onupdate="CASCADE",
#             ondelete="CASCADE",  # i.e. delete all possible values if the related coverage configuration gets deleted
#         ),
#         sqlalchemy.ForeignKeyConstraint(
#             [
#                 "forecast_model_id",
#             ],
#             [
#                 "forecastmodel.id",
#             ],
#             onupdate="CASCADE",
#             ondelete="CASCADE",  # i.e. delete all possible values if the related forecast model gets deleted
#         ),
#     )
#     forecast_coverage_configuration_id: Optional[int] = sqlmodel.Field(
#         # NOTE: foreign key already defined in __table_args__ in order to be able to
#         # specify the ondelete behavior
#         default=None,
#         primary_key=True,
#     )
#     forecast_model_id: Optional[int] = sqlmodel.Field(
#         # NOTE: foreign key already defined in __table_args__ in order to be able to
#         # specify the ondelete behavior
#         default=None,
#         primary_key=True,
#     )
#
#     forecast_coverage_configuration: "ForecastCoverageConfiguration" = (
#         sqlmodel.Relationship(back_populates="forecast_model_links")
#     )
#     forecast_model: ForecastModel = sqlmodel.Relationship(
#         back_populates="forecast_coverage_configuration_links"
#     )


class ForecastCoverageConfigurationForecastTimeWindowLink(
    sqlmodel.SQLModel, table=True
):
    __table_args__ = (
        sqlalchemy.ForeignKeyConstraint(
            [
                "forecast_coverage_configuration_id",
            ],
            [
                "forecastcoverageconfiguration.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete all possible values if the related coverage configuration gets deleted
        ),
        sqlalchemy.ForeignKeyConstraint(
            [
                "forecast_time_window_id",
            ],
            [
                "forecasttimewindow.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete all possible values if the related time window gets deleted
        ),
    )
    forecast_coverage_configuration_id: Optional[int] = sqlmodel.Field(
        # NOTE: foreign key already defined in __table_args__ in order to be able to
        # specify the ondelete behavior
        default=None,
        primary_key=True,
    )
    forecast_time_window_id: Optional[int] = sqlmodel.Field(
        # NOTE: foreign key already defined in __table_args__ in order to be able to
        # specify the ondelete behavior
        default=None,
        primary_key=True,
    )

    forecast_coverage_configuration: "ForecastCoverageConfiguration" = (
        sqlmodel.Relationship(back_populates="forecast_time_window_links")
    )
    forecast_time_window: ForecastTimeWindow = sqlmodel.Relationship(
        back_populates="forecast_coverage_configuration_links"
    )


class ForecastCoverageConfigurationObservationSeriesConfigurationLink(
    sqlmodel.SQLModel, table=True
):
    __table_args__ = (
        sqlalchemy.ForeignKeyConstraint(
            [
                "forecast_coverage_configuration_id",
            ],
            [
                "forecastcoverageconfiguration.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete all possible values if the related coverage configuration gets deleted
        ),
        sqlalchemy.ForeignKeyConstraint(
            [
                "observation_series_configuration_id",
            ],
            [
                "observationseriesconfiguration.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete all possible values if the related observation series configuration gets deleted
        ),
    )
    forecast_coverage_configuration_id: Optional[int] = sqlmodel.Field(
        # NOTE: foreign key already defined in __table_args__ in order to be able to
        # specify the ondelete behavior
        default=None,
        primary_key=True,
    )
    observation_series_configuration_id: Optional[int] = sqlmodel.Field(
        # NOTE: foreign key already defined in __table_args__ in order to be able to
        # specify the ondelete behavior
        default=None,
        primary_key=True,
    )

    forecast_coverage_configuration: "ForecastCoverageConfiguration" = (
        sqlmodel.Relationship(back_populates="observation_series_configuration_links")
    )
    observation_series_configuration: "observations.ObservationSeriesConfiguration" = (
        sqlmodel.Relationship(back_populates="forecast_coverage_configuration_links")
    )


class HistoricalCoverageConfigurationObservationSeriesConfigurationLink(
    sqlmodel.SQLModel, table=True
):
    __table_args__ = (
        sqlalchemy.ForeignKeyConstraint(
            [
                "historical_coverage_configuration_id",
            ],
            [
                "historicalcoverageconfiguration.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete all possible values if the related coverage configuration gets deleted
        ),
        sqlalchemy.ForeignKeyConstraint(
            [
                "observation_series_configuration_id",
            ],
            [
                "observationseriesconfiguration.id",
            ],
            onupdate="CASCADE",
            ondelete="CASCADE",  # i.e. delete all possible values if the related observation series configuration gets deleted
        ),
    )
    historical_coverage_configuration_id: Optional[int] = sqlmodel.Field(
        # NOTE: foreign key already defined in __table_args__ in order to be able to
        # specify the ondelete behavior
        default=None,
        primary_key=True,
    )
    observation_series_configuration_id: Optional[int] = sqlmodel.Field(
        # NOTE: foreign key already defined in __table_args__ in order to be able to
        # specify the ondelete behavior
        default=None,
        primary_key=True,
    )

    historical_coverage_configuration: "HistoricalCoverageConfiguration" = (
        sqlmodel.Relationship(back_populates="observation_series_configuration_links")
    )
    observation_series_configuration: "observations.ObservationSeriesConfiguration" = (
        sqlmodel.Relationship(back_populates="historical_coverage_configuration_links")
    )


class BaseCoverageConfiguration(sqlmodel.SQLModel):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    netcdf_main_dataset_name: str
    thredds_url_pattern: str
    climatic_indicator_id: Optional[int] = sqlmodel.Field(
        default=None, foreign_key="climaticindicator.id"
    )
    spatial_region_id: Optional[int] = sqlmodel.Field(
        default=None, foreign_key="spatialregion.id"
    )


class ForecastCoverageConfiguration(BaseCoverageConfiguration, table=True):
    forecast_model_group_id: Optional[int] = sqlmodel.Field(
        default=None, foreign_key="forecastmodelgroup.id"
    )
    year_period_group_id: Optional[int] = sqlmodel.Field(
        default=None, foreign_key="forecastyearperiodgroup.id"
    )
    wms_main_layer_name: str
    wms_secondary_layer_name: Optional[str] = None
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
    # year_periods: list[static.ForecastYearPeriod] = sqlmodel.Field(
    #     default=list,
    #     sa_column=sqlalchemy.Column(
    #         sqlmodel.ARRAY(sqlmodel.Enum(static.ForecastYearPeriod))
    #     ),
    # )
    # year_period_group_links: list[
    #     ForecastCoverageConfigurationForecastYearPeriodGroupLink
    # ] = sqlmodel.Relationship(back_populates="forecast_coverage_configurations")

    spatial_region: base.SpatialRegion = sqlmodel.Relationship(
        back_populates="forecast_coverage_configurations"
    )
    climatic_indicator: "climaticindicators.ClimaticIndicator" = sqlmodel.Relationship(
        back_populates="forecast_coverage_configurations"
    )

    # forecast_model_links: list[
    #     ForecastCoverageConfigurationForecastModelLink
    # ] = sqlmodel.Relationship(back_populates="forecast_coverage_configuration")

    # forecast_model_group_links: list[
    #     ForecastCoverageConfigurationForecastModelGroupLink
    # ] = sqlmodel.Relationship(back_populates="forecast_coverage_configuration")

    year_period_group: ForecastYearPeriodGroup = sqlmodel.Relationship(
        back_populates="forecast_coverage_configurations"
    )
    forecast_model_group: ForecastModelGroup = sqlmodel.Relationship(
        back_populates="forecast_coverage_configurations"
    )

    forecast_time_window_links: list[
        ForecastCoverageConfigurationForecastTimeWindowLink
    ] = sqlmodel.Relationship(
        back_populates="forecast_coverage_configuration",
    )
    observation_series_configuration_links: list[
        ForecastCoverageConfigurationObservationSeriesConfigurationLink
    ] = sqlmodel.Relationship(
        back_populates="forecast_coverage_configuration",
    )

    @pydantic.computed_field
    @property
    def identifier(self) -> str:
        return (
            "{data_category}-{climatic_indicator}-{spatial_region}-"
            "{year_period_group}-{forecast_model_group}".format(
                data_category=static.DataCategory.FORECAST.value,
                climatic_indicator=self.climatic_indicator.identifier,
                spatial_region=self.spatial_region.name,
                year_period_group=self.year_period_group.name,
                forecast_model_group=self.forecast_model_group.name,
            )
        )

    @staticmethod
    def get_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("forecast coverage configuration")

    @staticmethod
    def get_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("forecast coverage configuration description")


class ForecastCoverageConfigurationCreate(sqlmodel.SQLModel):
    netcdf_main_dataset_name: str
    thredds_url_pattern: str
    wms_main_layer_name: str
    wms_secondary_layer_name: Optional[str] = None
    climatic_indicator_id: int
    spatial_region_id: int
    lower_uncertainty_thredds_url_pattern: Optional[str] = None
    lower_uncertainty_netcdf_main_dataset_name: Optional[str] = None
    upper_uncertainty_thredds_url_pattern: Optional[str] = None
    upper_uncertainty_netcdf_main_dataset_name: Optional[str] = None
    scenarios: list[static.ForecastScenario]
    # year_periods: list[static.ForecastYearPeriod]
    year_period_group: int
    forecast_model_group: int
    forecast_time_windows: Optional[list[int]] = None
    observation_series_configurations: Optional[list[int]] = None


class ForecastCoverageConfigurationUpdate(sqlmodel.SQLModel):
    netcdf_main_dataset_name: Optional[str] = None
    thredds_url_pattern: Optional[str] = None
    wms_main_layer_name: Optional[str] = None
    wms_secondary_layer_name: Optional[str] = None
    climatic_indicator_id: Optional[int] = None
    spatial_region_id: Optional[int] = None
    lower_uncertainty_thredds_url_pattern: Optional[str] = None
    lower_uncertainty_netcdf_main_dataset_name: Optional[str] = None
    upper_uncertainty_thredds_url_pattern: Optional[str] = None
    upper_uncertainty_netcdf_main_dataset_name: Optional[str] = None
    scenarios: Optional[list[static.ForecastScenario]] = None
    # year_periods: Optional[list[static.ForecastYearPeriod]] = None
    year_period_group: Optional[int] = None
    forecast_model_group: Optional[int] = None
    forecast_time_windows: Optional[list[int]] = None
    observation_series_configurations: Optional[list[int]] = None


@dataclasses.dataclass(frozen=True)
class ForecastCoverageInternal:
    configuration: ForecastCoverageConfiguration
    scenario: static.ForecastScenario
    forecast_model: ForecastModel
    year_period: static.ForecastYearPeriod
    forecast_time_window: Optional[ForecastTimeWindow] = None

    def __post_init__(self):
        error_message = "{param} {value!r} is not part of the forecast coverage configuration {conf!r}"
        if self.scenario not in self.configuration.scenarios:
            raise exceptions.InvalidForecastScenarioError(
                error_message.format(
                    param="scenario",
                    value=self.scenario.value,
                    conf=self.configuration.identifier,
                )
            )
        if self.forecast_model.id not in (
            fml.forecast_model_id
            for fml in self.configuration.forecast_model_group.forecast_model_links
        ):
            raise exceptions.InvalidForecastModelError(
                error_message.format(
                    param="forecast model",
                    value=self.forecast_model.name,
                    conf=self.configuration.identifier,
                )
            )
        if self.year_period not in self.configuration.year_period_group.year_periods:
            raise exceptions.InvalidForecastYearPeriodError(
                error_message.format(
                    param="year period",
                    value=self.year_period.value,
                    conf=self.configuration.identifier,
                )
            )
        if self.forecast_time_window is not None:
            if self.forecast_time_window.id not in (
                twl.forecast_time_window_id
                for twl in self.configuration.forecast_time_window_links
            ):
                raise exceptions.InvalidForecastTimeWindowError(
                    error_message.format(
                        param="forecast time window",
                        value=self.forecast_time_window.name,
                        conf=self.configuration.identifier,
                    )
                )

    @property
    def identifier(self) -> str:
        pattern_parts = [
            self.configuration.identifier,
            self.forecast_model.name,
            self.scenario.value,
            self.year_period.value,
        ]
        if self.forecast_time_window is not None:
            pattern_parts.append(self.forecast_time_window.name)
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

    def get_thredds_file_download_url(
        self, settings: ThreddsServerSettings
    ) -> Optional[str]:
        return crawler.get_file_download_url(self._get_thredds_url_fragment(), settings)

    def get_lower_uncertainty_thredds_file_download_url(
        self, settings: ThreddsServerSettings
    ) -> Optional[str]:
        rendered = self._get_lower_uncertainty_thredds_url_fragment()
        return crawler.get_file_download_url(rendered, settings) if rendered else None

    def get_upper_uncertainty_thredds_file_download_url(
        self, settings: ThreddsServerSettings
    ) -> Optional[str]:
        rendered = self._get_upper_uncertainty_thredds_url_fragment()
        return crawler.get_file_download_url(rendered, settings) if rendered else None

    def get_wms_base_url(self, settings: ThreddsServerSettings) -> Optional[str]:
        return crawler.get_wms_base_url(self._get_thredds_url_fragment(), settings)

    def get_thredds_ncss_url(self, settings: ThreddsServerSettings) -> Optional[str]:
        return crawler.get_ncss_url(self._get_thredds_url_fragment(), settings)

    def get_lower_uncertainty_thredds_ncss_url(
        self, settings: ThreddsServerSettings
    ) -> Optional[str]:
        rendered = self._get_lower_uncertainty_thredds_url_fragment()
        return crawler.get_ncss_url(rendered, settings) if rendered else None

    def get_upper_uncertainty_thredds_ncss_url(
        self, settings: ThreddsServerSettings
    ) -> Optional[str]:
        rendered = self._get_upper_uncertainty_thredds_url_fragment()
        return crawler.get_ncss_url(rendered, settings) if rendered else None

    def get_wms_main_layer_name(self) -> str:
        return self._render_templated_value(self.configuration.wms_main_layer_name)

    def get_wms_secondary_layer_name(self) -> Optional[str]:
        return self._render_templated_value(self.configuration.wms_secondary_layer_name)

    def _get_forecast_model_thredds_url_base_path(self) -> Optional[str]:
        result = None
        for fml in self.configuration.climatic_indicator.forecast_model_links:
            if fml.forecast_model_id == self.forecast_model.id:
                result = fml.thredds_url_base_path
                break
        return result

    def _get_forecast_model_thredds_url_uncertainties_base_path(self) -> Optional[str]:
        result = None
        for fml in self.configuration.climatic_indicator.forecast_model_links:
            if fml.forecast_model_id == self.forecast_model.id:
                result = fml.thredds_url_uncertainties_base_path
                break
        return result

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
        forecast_model_base_path = self._get_forecast_model_thredds_url_base_path()
        uncertainties_base_path = (
            self._get_forecast_model_thredds_url_uncertainties_base_path()
        )
        return value.format(
            forecast_model_base_path=(
                forecast_model_base_path if forecast_model_base_path is not None else ""
            ),
            forecast_model_uncertainties_base_path=(
                uncertainties_base_path if uncertainties_base_path is not None else ""
            ),
            forecast_model=self.forecast_model.internal_value,
            climatic_indicator=self.configuration.climatic_indicator.name,
            time_window=(
                self.forecast_time_window.internal_value
                if self.forecast_time_window is not None
                else ""
            ),
            scenario=self.scenario.get_internal_value(),
            year_period=self.year_period.get_internal_value(),
            spatial_region=self.configuration.spatial_region.internal_value,
        )

    def __hash__(self):
        return hash(self.identifier)


class HistoricalCoverageConfiguration(BaseCoverageConfiguration, table=True):
    year_period_group_id: Optional[int] = sqlmodel.Field(
        default=None, foreign_key="historicalyearperiodgroup.id"
    )
    reference_period: Optional[static.HistoricalReferencePeriod]
    wms_main_layer_name: str
    decades: list[static.HistoricalDecade] = sqlmodel.Field(
        default=list,
        sa_column=sqlalchemy.Column(
            sqlmodel.ARRAY(sqlmodel.Enum(static.HistoricalDecade))
        ),
    )
    # year_periods: list[static.HistoricalYearPeriod] = sqlmodel.Field(
    #     default=list,
    #     sa_column=sqlalchemy.Column(
    #         sqlmodel.ARRAY(sqlmodel.Enum(static.HistoricalYearPeriod))
    #     ),
    # )
    # historical_year_period_group_links: list[
    #     HistoricalCoverageConfigurationHistoricalYearPeriodGroupLink
    # ] = sqlmodel.Relationship(back_populates="historical_coverage_configurations")

    spatial_region: base.SpatialRegion = sqlmodel.Relationship(
        back_populates="historical_coverage_configurations"
    )
    climatic_indicator: "climaticindicators.ClimaticIndicator" = sqlmodel.Relationship(
        back_populates="historical_coverage_configurations"
    )

    year_period_group: HistoricalYearPeriodGroup = sqlmodel.Relationship(
        back_populates="historical_coverage_configurations"
    )

    observation_series_configuration_links: list[
        HistoricalCoverageConfigurationObservationSeriesConfigurationLink
    ] = sqlmodel.Relationship(
        back_populates="historical_coverage_configuration",
    )

    @pydantic.computed_field
    @property
    def identifier(self) -> str:
        return (
            "{data_category}-{climatic_indicator}-"
            "{spatial_region}-{year_period_group}{extra}".format(
                data_category=static.DataCategory.HISTORICAL.value,
                climatic_indicator=self.climatic_indicator.identifier,
                spatial_region=self.spatial_region.name,
                year_period_group=self.year_period_group.name,
                extra=(
                    f"-{self.reference_period.value}"
                    if self.reference_period is not None
                    else ""
                ),
            )
        )

    @staticmethod
    def get_display_name(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("historical coverage configuration")

    @staticmethod
    def get_description(locale: babel.Locale) -> str:
        translations = get_translations(locale)
        _ = translations.gettext
        return _("historical coverage configuration description")


class HistoricalCoverageConfigurationCreate(sqlmodel.SQLModel):
    netcdf_main_dataset_name: str
    thredds_url_pattern: str
    wms_main_layer_name: str
    climatic_indicator_id: int
    spatial_region_id: int
    reference_period: Optional[static.HistoricalReferencePeriod] = None
    decades: Optional[list[static.HistoricalDecade]] = None
    year_period_group: int
    observation_series_configurations: Optional[list[int]] = None


class HistoricalCoverageConfigurationUpdate(sqlmodel.SQLModel):
    netcdf_main_dataset_name: Optional[str] = None
    thredds_url_pattern: Optional[str] = None
    wms_main_layer_name: Optional[str] = None
    climatic_indicator_id: Optional[int] = None
    spatial_region_id: Optional[int] = None
    reference_period: Optional[static.HistoricalReferencePeriod] = None
    decades: Optional[list[static.HistoricalDecade]] = None
    year_period_group: Optional[int] = None
    observation_series_configurations: Optional[list[int]] = None


@dataclasses.dataclass(frozen=True)
class HistoricalCoverageInternal:
    configuration: HistoricalCoverageConfiguration
    year_period: static.HistoricalYearPeriod
    decade: Optional[static.HistoricalDecade] = None

    def __post_init__(self):
        error_message = "{param} {value!r} is not part of the historical coverage configuration {conf!r}"
        if self.year_period not in self.configuration.year_period_group.year_periods:
            raise exceptions.InvalidForecastYearPeriodError(
                error_message.format(
                    param="year period",
                    value=self.year_period.value,
                    conf=self.configuration.identifier,
                )
            )
        if self.decade is not None and self.decade not in self.configuration.decades:
            raise exceptions.InvalidHistoricalDecade(
                error_message.format(
                    param="decade",
                    value=self.decade.value,
                    conf=self.configuration.identifier,
                )
            )

    @property
    def identifier(self) -> str:
        pattern_parts = [
            self.configuration.identifier,
            self.year_period.value,
        ]
        if self.decade is not None:
            pattern_parts.append(self.decade.value)
        return "-".join(pattern_parts)

    def get_netcdf_main_dataset_name(self) -> str:
        return self._render_templated_value(self.configuration.netcdf_main_dataset_name)

    def get_thredds_file_download_url(
        self, settings: ThreddsServerSettings
    ) -> Optional[str]:
        return crawler.get_file_download_url(self._get_thredds_url_fragment(), settings)

    def get_wms_base_url(self, settings: ThreddsServerSettings) -> Optional[str]:
        return crawler.get_wms_base_url(self._get_thredds_url_fragment(), settings)

    def get_thredds_ncss_url(self, settings: ThreddsServerSettings) -> Optional[str]:
        return crawler.get_ncss_url(self._get_thredds_url_fragment(), settings)

    def get_wms_main_layer_name(self) -> str:
        return self._render_templated_value(self.configuration.wms_main_layer_name)

    def _get_thredds_url_fragment(self) -> str:
        return self._render_templated_value(self.configuration.thredds_url_pattern)

    def _render_templated_value(self, value: str) -> str:
        return value.format(
            climatic_indicator=(
                self.configuration.climatic_indicator.historical_coverages_internal_name
            ),
            year_period=self.year_period.get_internal_value(),
            decade=self.decade.get_internal_value() if self.decade else "",
            reference_period=(
                self.configuration.reference_period.get_internal_value()
                if self.configuration.reference_period is not None
                else ""
            ),
            spatial_region=self.configuration.spatial_region.internal_value,
        )

    def __hash__(self):
        return hash(self.identifier)


@dataclasses.dataclass(frozen=True)
class LegacyConfParamFilterValues:
    aggregation_period: Optional[static.AggregationPeriod]  # done
    archive: Optional[str]
    climatological_model: Optional[ForecastModel]
    climatological_variable: Optional[str]
    historical_decade: Optional[static.HistoricalDecade]
    historical_reference_period: Optional[static.HistoricalDecade]
    historical_variable: Optional[str]
    historical_year_period: Optional[static.HistoricalYearPeriod]
    measure: Optional[static.MeasureType]
    scenario: Optional[static.ForecastScenario]
    uncertainty_type: Optional[str]
    time_window: Optional[ForecastTimeWindow]
    year_period: Optional[static.ForecastYearPeriod]
    climatic_indicator: Optional["climaticindicators.ClimaticIndicator"]
