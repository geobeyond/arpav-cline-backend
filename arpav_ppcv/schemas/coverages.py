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

import pydantic
import sqlalchemy
import sqlmodel

from .. import exceptions
from . import base

if TYPE_CHECKING:
    from . import observations

logger = logging.getLogger(__name__)
_NAME_PATTERN: Final[str] = r"^[a-z0-9_]+$"


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
    used_in_configurations: "ConfigurationParameterPossibleValue" = sqlmodel.Relationship(
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
    display_name_english: Optional[str] = None
    display_name_italian: Optional[str] = None
    description_english: Optional[str] = None
    description_italian: Optional[str] = None
    netcdf_main_dataset_name: str
    thredds_url_pattern: str
    wms_main_layer_name: Optional[str] = None
    wms_secondary_layer_name: Optional[str] = None
    unit_english: str = ""
    unit_italian: Optional[str] = None
    palette: str
    color_scale_min: float = 0.0
    color_scale_max: float = 1.0
    data_precision: int = 3
    observation_variable_id: Optional[uuid.UUID] = sqlmodel.Field(
        default=None, foreign_key="variable.id"
    )
    observation_variable_aggregation_type: Optional[
        base.ObservationAggregationType
    ] = None
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

    related_observation_variable: "observations.Variable" = sqlmodel.Relationship(
        back_populates="related_coverage_configurations"
    )

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
        for pv in self.possible_values:
            other_parts.add(
                pv.configuration_parameter_value.configuration_parameter.name
            )
        all_parts = ["name"] + sorted(list(other_parts))
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
        rendered = template
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
        id_parts = [self.name]
        for match_obj in re.finditer(r"(\{\w+\})", self.coverage_id_pattern):
            param_name = match_obj.group(1)[1:-1]
            if param_name != "name":
                for conf_param_value in parameters:
                    conf_param = conf_param_value.configuration_parameter
                    if conf_param.name == param_name:
                        id_parts.append(conf_param_value.name)
                        break
                else:
                    raise ValueError(
                        f"Could not find suitable value for {param_name!r}"
                    )
            else:
                continue
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
        pattern_parts = re.finditer(
            r"\{(\w+)\}", self.coverage_id_pattern.partition("-")[-1]
        )
        id_parts = coverage_identifier.split("-")[1:]
        result = {}
        for index, pattern_match_obj in enumerate(pattern_parts):
            configuration_parameter_name = pattern_match_obj.group(1)
            id_part = id_parts[index]
            result[configuration_parameter_name] = id_part
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
    display_name_english: Optional[str] = None
    display_name_italian: Optional[str] = None
    description_english: Optional[str] = None
    description_italian: Optional[str] = None
    netcdf_main_dataset_name: str
    # the point in having a wms_main_layer_name and wms_secondary_layer_name is to let
    # the frontend toggle between them
    wms_main_layer_name: Optional[str] = None
    wms_secondary_layer_name: Optional[str] = None
    thredds_url_pattern: str
    unit_english: str
    unit_italian: Optional[str] = None
    palette: str
    color_scale_min: float
    color_scale_max: float
    data_precision: int = 3
    possible_values: list["ConfigurationParameterPossibleValueCreate"]
    observation_variable_id: Optional[uuid.UUID] = None
    observation_variable_aggregation_type: Optional[
        base.ObservationAggregationType
    ] = None
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
    display_name_english: Optional[str] = None
    display_name_italian: Optional[str] = None
    description_english: Optional[str] = None
    description_italian: Optional[str] = None
    netcdf_main_dataset_name: Optional[str] = None
    wms_main_layer_name: Optional[str] = None
    wms_secondary_layer_name: Optional[str] = None
    thredds_url_pattern: Optional[str] = None
    unit_english: Optional[str] = None
    unit_italian: Optional[str] = None
    palette: Optional[str] = None
    color_scale_min: Optional[float] = None
    color_scale_max: Optional[float] = None
    data_precision: Optional[int] = None
    observation_variable_id: Optional[uuid.UUID] = None
    observation_variable_aggregation_type: Optional[
        base.ObservationAggregationType
    ] = None
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


class ForecastVariableMenuTree(TypedDict):
    climatological_variable: ConfigurationParameterValue
    aggregation_period: ConfigurationParameterValue
    measure: ConfigurationParameterValue
    combinations: dict[str, VariableMenuTreeCombination]


class HistoricalVariableMenuTree(TypedDict):
    historical_variable: ConfigurationParameterValue
    aggregation_period: ConfigurationParameterValue
    combinations: dict[str, VariableMenuTreeCombination]
