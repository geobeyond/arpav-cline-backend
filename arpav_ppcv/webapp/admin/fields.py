import logging
from typing import Any

import starlette_admin
from starlette.requests import Request

from ... import database
from . import schemas as read_schemas

logger = logging.getLogger(__name__)


class UuidField(starlette_admin.StringField):
    """Custom field for handling item identifiers.

    This field, in conjunction with the custom collection template, ensures
    that we can have related fields be edited inline, by sending the item's `id`
    as a form hidden field.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.input_type = "hidden"

    async def serialize_value(
        self, request: Request, value: Any, action: starlette_admin.RequestAction
    ) -> Any:
        return str(value)


class PossibleConfigurationParameterValuesField(starlette_admin.EnumField):
    def _get_label(
        self,
        value: read_schemas.ConfigurationParameterPossibleValueRead,
        request: Request,
    ) -> Any:
        conf_parameter_value = database.get_configuration_parameter_value(
            request.state.session, value.configuration_parameter_value_id
        )
        result = " - ".join(
            (
                conf_parameter_value.configuration_parameter.name,
                conf_parameter_value.name,
            )
        )
        return result

    async def serialize_value(
        self,
        request: Request,
        value: read_schemas.ConfigurationParameterPossibleValueRead,
        action: starlette_admin.RequestAction,
    ) -> Any:
        return self._get_label(value, request)


class RelatedClimaticIndicatorField(starlette_admin.EnumField):
    """Custom field to show a 1:m relationship.

    This somewhat abuses the default way to represent relationships in starlete_admin.
    However, it provides more control over presentation of data.

    Things to consider here are:

    - overriding `__post_init__()` as a way to define `choices_loader` together with
    the custom field - the alternative would be to write the choices loader as a
    standalone function and then use it in the field initializer, which would
    put them in different files.

    - overriding `get_label()` as way to use the climatic_identifier.identifier field
    as a friendlier way to refer to the instance in forms

    """

    def __post_init__(self) -> None:
        self.choices_loader = RelatedClimaticIndicatorField.choices_loader
        super().__post_init__()

    def _get_label(self, value: int, request: Request) -> str:
        session = request.state.session
        climatic_indicator = database.get_climatic_indicator(session, value)
        return climatic_indicator.identifier

    @staticmethod
    def choices_loader(request: Request):
        all_climatic_indicators = database.collect_all_climatic_indicators(
            request.state.session
        )
        return [(ci.id, ci.identifier) for ci in all_climatic_indicators]


class RelatedObservationsVariableField(starlette_admin.EnumField):
    def _get_label(
        self, value: read_schemas.ObservationVariableRead, request: Request
    ) -> Any:
        return value.name

    async def serialize_value(
        self,
        request: Request,
        value: read_schemas.ObservationVariableRead,
        action: starlette_admin.RequestAction,
    ) -> Any:
        return self._get_label(value, request)


class RelatedCoverageconfigurationsField(starlette_admin.EnumField):
    def _get_label(
        self, value: read_schemas.CoverageConfigurationReadListItem, request: Request
    ) -> Any:
        return value.name

    async def serialize_value(
        self,
        request: Request,
        value: read_schemas.CoverageConfigurationReadListItem,
        action: starlette_admin.RequestAction,
    ) -> Any:
        return self._get_label(value, request)
