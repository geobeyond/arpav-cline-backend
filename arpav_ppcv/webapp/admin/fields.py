from typing import Any

import starlette_admin
from starlette.requests import Request

from ... import database
from . import schemas as read_schemas


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
