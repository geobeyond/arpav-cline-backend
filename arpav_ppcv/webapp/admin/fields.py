import logging
from typing import Any

import starlette_admin
from starlette.requests import Request

import arpav_ppcv.db.legacy
from ... import db
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
        conf_parameter_value = arpav_ppcv.db.legacy.get_configuration_parameter_value(
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


class RelatedForecastModelGroupField(starlette_admin.EnumField):
    def __post_init__(self) -> None:
        self.choices_loader = RelatedForecastModelGroupField.choices_loader
        super().__post_init__()

    def _get_label(self, value: int, request: Request) -> str:
        session = request.state.session
        db_forecast_model_group = db.get_forecast_model_group(session, value)
        return db_forecast_model_group.name

    async def serialize_value(
        self,
        request: Request,
        value: int,
        action: starlette_admin.RequestAction,
    ) -> Any:
        return self._get_label(value, request)

    @staticmethod
    def choices_loader(request: Request):
        all_forecast_model_groups = db.collect_all_forecast_model_groups(
            request.state.session
        )
        return [(str(fmg.id), fmg.name) for fmg in all_forecast_model_groups]


class RelatedForecastYearPeriodGroupField(starlette_admin.EnumField):
    def __post_init__(self) -> None:
        self.choices_loader = RelatedForecastYearPeriodGroupField.choices_loader
        super().__post_init__()

    def _get_label(self, value: int, request: Request) -> str:
        session = request.state.session
        db_year_period_group = db.get_forecast_year_period_group(session, value)
        return db_year_period_group.name

    async def serialize_value(
        self,
        request: Request,
        value: int,
        action: starlette_admin.RequestAction,
    ) -> Any:
        return self._get_label(value, request)

    @staticmethod
    def choices_loader(request: Request):
        all_year_period_groups = db.collect_all_forecast_year_period_groups(
            request.state.session
        )
        return [(str(ypg.id), ypg.name) for ypg in all_year_period_groups]


class RelatedHistoricalYearPeriodGroupField(starlette_admin.EnumField):
    def __post_init__(self) -> None:
        self.choices_loader = RelatedHistoricalYearPeriodGroupField.choices_loader
        super().__post_init__()

    def _get_label(self, value: int, request: Request) -> str:
        session = request.state.session
        db_year_period_group = db.get_historical_year_period_group(session, value)
        return db_year_period_group.name

    async def serialize_value(
        self,
        request: Request,
        value: int,
        action: starlette_admin.RequestAction,
    ) -> Any:
        return self._get_label(value, request)

    @staticmethod
    def choices_loader(request: Request):
        all_year_period_groups = db.collect_all_historical_year_period_groups(
            request.state.session
        )
        return [(str(ypg.id), ypg.name) for ypg in all_year_period_groups]


class RelatedForecastModelField(starlette_admin.EnumField):
    def __post_init__(self) -> None:
        self.choices_loader = RelatedForecastModelField.choices_loader
        super().__post_init__()

    # def _get_label(self, value: int, request: Request) -> str:
    #     session = request.state.session
    #     db_forecast_model = db.get_forecast_model(session, value)
    #     return db_forecast_model.name

    # async def serialize_value(
    #     self,
    #     request: Request,
    #     value: int,
    #     action: starlette_admin.RequestAction,
    # ) -> Any:
    #     logger.debug(f"{value=}")
    #     return self._get_label(value, request)

    @staticmethod
    def choices_loader(request: Request):
        all_forecast_models = db.collect_all_forecast_models(request.state.session)
        return [(fm.id, fm.name) for fm in all_forecast_models]


class RelatedForecastModelsField(starlette_admin.EnumField):
    def __post_init__(self) -> None:
        self.choices_loader = RelatedForecastModelsField.choices_loader
        super().__post_init__()

    def _get_label(self, value: int, request: Request) -> str:
        result = None
        for v, label in self._get_choices(request):
            if value == v:
                result = label
                break
        return result

    async def serialize_value(
        self, request: Request, value: Any, action: starlette_admin.RequestAction
    ) -> Any:
        labels = [
            (
                self._get_label(v, request)
                if action != starlette_admin.RequestAction.EDIT
                else v
            )
            for v in (value if self.multiple else [value])
        ]
        return labels if self.multiple else labels[0]

    @staticmethod
    def choices_loader(request: Request):
        all_forecast_models = db.collect_all_forecast_models(request.state.session)
        result = [(fm.id, fm.name) for fm in all_forecast_models]
        return result


class RelatedForecastTimeWindowField(starlette_admin.EnumField):
    def __post_init__(self) -> None:
        self.choices_loader = RelatedForecastTimeWindowField.choices_loader
        super().__post_init__()

    def _get_label(self, value: int, request: Request) -> str:
        session = request.state.session
        db_forecast_time_window = db.get_forecast_time_window(session, value)
        return db_forecast_time_window.name

    async def serialize_value(
        self,
        request: Request,
        value: int,
        action: starlette_admin.RequestAction,
    ) -> Any:
        return self._get_label(value, request)

    @staticmethod
    def choices_loader(request: Request):
        all_forecast_time_windows = db.collect_all_forecast_time_windows(
            request.state.session
        )
        return [(str(tw.id), tw.name) for tw in all_forecast_time_windows]


class RelatedObservationSeriesConfigurationField(starlette_admin.EnumField):
    def __post_init__(self) -> None:
        self.choices_loader = RelatedObservationSeriesConfigurationField.choices_loader
        super().__post_init__()

    def _get_label(self, value: int, request: Request) -> str:
        session = request.state.session
        db_observation_series_configuration = db.get_observation_series_configuration(
            session, value
        )
        return db_observation_series_configuration.identifier

    async def serialize_value(
        self,
        request: Request,
        value: int,
        action: starlette_admin.RequestAction,
    ) -> Any:
        return self._get_label(value, request)

    @staticmethod
    def choices_loader(request: Request):
        all_obs_series_confs = db.collect_all_observation_series_configurations(
            request.state.session
        )
        return [(str(osc.id), osc.identifier) for osc in all_obs_series_confs]


class RelatedObservationStationField(starlette_admin.EnumField):
    def __post_init__(self) -> None:
        self.choices_loader = RelatedObservationStationField.choices_loader
        super().__post_init__()

    def _get_label(self, value: int, request: Request) -> str:
        session = request.state.session
        observation_station = db.get_observation_station(session, value)
        return observation_station.code

    async def serialize_value(
        self,
        request: Request,
        value: int,
        action: starlette_admin.RequestAction,
    ) -> Any:
        return self._get_label(value, request)

    @staticmethod
    def choices_loader(request: Request) -> list[tuple[int, str]]:
        all_stations = db.collect_all_observation_stations(request.state.session)
        return [(s.id, s.name) for s in all_stations]


class RelatedSpatialRegionField(starlette_admin.EnumField):
    def __post_init__(self) -> None:
        self.choices_loader = RelatedSpatialRegionField.choices_loader
        super().__post_init__()

    def _get_label(self, value: int, request: Request) -> str:
        session = request.state.session
        spatial_region = db.get_spatial_region(session, value)
        return spatial_region.name

    async def serialize_value(
        self,
        request: Request,
        value: int,
        action: starlette_admin.RequestAction,
    ) -> Any:
        return self._get_label(value, request)

    @staticmethod
    def choices_loader(request: Request):
        all_spatial_regions = db.collect_all_spatial_regions(request.state.session)
        return [(sr.id, sr.name) for sr in all_spatial_regions]


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
        climatic_indicator = db.get_climatic_indicator(session, value)
        return climatic_indicator.identifier

    async def serialize_value(
        self,
        request: Request,
        value: int,
        action: starlette_admin.RequestAction,
    ) -> Any:
        return self._get_label(value, request)

    @staticmethod
    def choices_loader(request: Request):
        all_climatic_indicators = db.collect_all_climatic_indicators(
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
