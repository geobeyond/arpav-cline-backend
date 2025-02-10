"""Views for the admin app's coverages.

The classes contained in this module are derived from
starlette_admin.contrib.sqlmodel.ModelView. This is done mostly for two reasons:

1. To be able to control database access and ensure we are using our handlers
   defined in `arpav_ppcv.database` - this is meant for achieving consistency
   throughout the code, as the API is also using the mentioned functions for
   interacting with the DB

2. To be able to present inline forms for editing related objects, as is the
   case with parameter configuration and its related values.

"""

import functools
import logging
import uuid
from typing import Dict, Any, Union, Optional, List, Sequence

import anyio.to_thread
import starlette_admin
from starlette.requests import Request
from starlette_admin import exceptions as starlette_admin_exceptions
from starlette_admin.contrib.sqlmodel import ModelView

from .... import database
from ....schemas import (
    coverages,
    base,
)
from .. import (
    fields,
    schemas as read_schemas,
)


logger = logging.getLogger(__name__)


def possible_values_choices_loader(request: Request) -> Sequence[tuple[str, str]]:
    all_conf_parameter_values = database.collect_all_configuration_parameter_values(
        request.state.session
    )
    result = []
    for conf_param_value in all_conf_parameter_values:
        repr_value = " - ".join(
            (conf_param_value.configuration_parameter.name, conf_param_value.name)
        )
        result.append((repr_value, repr_value))
    return result


def related_observation_variable_choices_loader(
    request: Request,
) -> Sequence[tuple[str, str]]:
    all_obs_variables = database.collect_all_variables(request.state.session)
    return [(v.name, v.name) for v in all_obs_variables]


def coverage_configurations_choices_loader(
    request: Request,
) -> Sequence[tuple[str, str]]:
    if (pk := request.path_params.get("pk")) is not None:
        main_cov_conf_id = uuid.UUID(pk)
    else:
        main_cov_conf_id = None
    result = []
    all_cov_confs = database.collect_all_coverage_configurations(request.state.session)
    for cov_conf in [cc for cc in all_cov_confs if cc.id != main_cov_conf_id]:
        result.append((cov_conf.name, cov_conf.name))
    return result


class ConfigurationParameterView(ModelView):
    identity = "configuration_parameters"
    name = "Configuration Parameter"
    label = "Configuration Parameters"
    icon = "fa fa-blog"
    pk_attr = "id"

    exclude_fields_from_list = (
        "id",
        "allowed_values",
        "display_name_english",
        "display_name_italian",
        "description_english",
        "description_italian",
    )
    exclude_fields_from_detail = ("id",)

    fields = (
        fields.UuidField("id"),
        starlette_admin.StringField(
            "name",
            help_text=(
                "Name for the configuration parameter. Must only use alphanumeric "
                "characters and the underscore. If you use the special name "
                "'year_period', then the system will use this parameter to "
                "perform database queries."
            ),
        ),
        starlette_admin.StringField("display_name_english", required=True),
        starlette_admin.StringField("display_name_italian", required=True),
        starlette_admin.StringField("description_english"),
        starlette_admin.StringField("description_italian"),
        starlette_admin.ListField(
            field=starlette_admin.CollectionField(
                "allowed_values",
                fields=(
                    fields.UuidField(
                        "id",
                        read_only=True,
                        # disabled=True,
                        exclude_from_list=True,
                        exclude_from_detail=True,
                        exclude_from_create=True,
                        exclude_from_edit=False,
                    ),
                    starlette_admin.StringField("internal_value", required=True),
                    starlette_admin.StringField("name"),
                    starlette_admin.StringField("display_name_english", required=True),
                    starlette_admin.StringField("display_name_italian", required=True),
                    starlette_admin.StringField("description_english"),
                    starlette_admin.StringField("description_italian"),
                    starlette_admin.StringField("sort_order"),
                ),
            )
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon = "fa-solid fa-quote-left"

    async def get_pk_value(self, request: Request, obj: Any) -> Any:
        # note: we need to cast the value, which is a uuid.UUID, to a string
        # because starlette_admin just assumes that the value of a model's
        # pk attribute is always JSON serializable so it doesn't bother with
        # calling the respective field's `serialize_value()` method
        result = await super().get_pk_value(request, obj)
        return str(result)

    async def create(self, request: Request, data: Dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data)
            await self.validate(request, data)
            config_param_create = coverages.ConfigurationParameterCreate(
                name=data["name"],
                display_name_english=data["display_name_english"],
                display_name_italian=data["display_name_italian"],
                description_english=data.get("description_english"),
                description_italian=data.get("description_italian"),
                allowed_values=[
                    coverages.ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                        internal_value=av["internal_value"],
                        name=av.get("name") or av["internal_value"].replace("-", "_"),
                        display_name_english=av["display_name_english"],
                        display_name_italian=av["display_name_italian"],
                        description_english=av.get("description_english"),
                        description_italian=av.get("description_italian"),
                        sort_order=av.get("sort_order", 0),
                    )
                    for av in data["allowed_values"]
                ],
            )
            db_configuration_parameter = await anyio.to_thread.run_sync(
                database.create_configuration_parameter,
                request.state.session,
                config_param_create,
            )
            configuration_parameter_read = read_schemas.ConfigurationParameterRead(
                **db_configuration_parameter.model_dump(exclude={"allowed_values"}),
                allowed_values=[
                    read_schemas.ConfigurationParameterValueRead(**av.model_dump())
                    for av in db_configuration_parameter.allowed_values
                ],
            )
            logger.debug("About to leave the create instance")
            logger.debug(f"{configuration_parameter_read=}")
            return configuration_parameter_read
        except Exception as e:
            return self.handle_exception(e)

    async def check_modifications_to_core_configuration_parameters(
        self,
        request: Request,
        pk: uuid.UUID,
        data: Dict[str, Any],
    ):
        conf_param = await anyio.to_thread.run_sync(
            database.get_configuration_parameter, request.state.session, pk
        )
        if conf_param.name in [p.value for p in base.CoreConfParamName]:
            if data.get("name") != conf_param.name:
                raise starlette_admin_exceptions.FormValidationError(
                    errors={
                        "name": (
                            f"Cannot change parameter {conf_param.name!r}'s name - it "
                            f"is a core system parameter"
                        )
                    }
                )

    async def edit(self, request: Request, pk: Any, data: Dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data, True)
            await self.validate(request, data)
            await self.check_modifications_to_core_configuration_parameters(
                request, pk, data
            )
            config_param_update = coverages.ConfigurationParameterUpdate(
                name=data.get("name"),
                display_name_english=data["display_name_english"],
                display_name_italian=data["display_name_italian"],
                description_english=data.get("description_english"),
                description_italian=data.get("description_italian"),
                allowed_values=[
                    coverages.ConfigurationParameterValueUpdateEmbeddedInConfigurationParameterEdit(
                        id=av["id"] or None,
                        internal_value=av["internal_value"],
                        name=av.get("name") or av["internal_value"].replace("-", "_"),
                        display_name_english=av["display_name_english"],
                        display_name_italian=av["display_name_italian"],
                        description_english=av.get("description_english"),
                        description_italian=av.get("description_italian"),
                        sort_order=av.get("sort_order"),
                    )
                    for av in data["allowed_values"]
                ],
            )
            db_configuration_parameter = await anyio.to_thread.run_sync(
                database.get_configuration_parameter, request.state.session, pk
            )
            db_configuration_parameter = await anyio.to_thread.run_sync(
                database.update_configuration_parameter,
                request.state.session,
                db_configuration_parameter,
                config_param_update,
            )
            conf_param_read = read_schemas.ConfigurationParameterRead(
                **db_configuration_parameter.model_dump(),
                allowed_values=[
                    read_schemas.ConfigurationParameterValueRead(**av.model_dump())
                    for av in db_configuration_parameter.allowed_values
                ],
            )
            return conf_param_read
        except Exception as e:
            logger.exception("something went wrong")
            self.handle_exception(e)

    async def find_by_pk(
        self, request: Request, pk: Any
    ) -> read_schemas.ConfigurationParameterRead:
        db_conf_param = await anyio.to_thread.run_sync(
            database.get_configuration_parameter, request.state.session, pk
        )
        allowed = []
        for av in db_conf_param.allowed_values:
            cpv_kwargs = av.model_dump()
            cpv_kwargs["sort_order"] = cpv_kwargs["sort_order"] or 0
            allowed.append(read_schemas.ConfigurationParameterValueRead(**cpv_kwargs))
        return read_schemas.ConfigurationParameterRead(
            **db_conf_param.model_dump(),
            allowed_values=allowed,
        )

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[Dict[str, Any], str, None] = None,
        order_by: Optional[List[str]] = None,
    ) -> Sequence[read_schemas.ConfigurationParameterRead]:
        list_params = functools.partial(
            database.list_configuration_parameters,
            limit=limit,
            offset=skip,
            name_filter=str(where) if where not in (None, "") else None,
            include_total=False,
        )
        db_conf_params, _ = await anyio.to_thread.run_sync(
            list_params, request.state.session
        )
        result = []
        for db_conf_param in db_conf_params:
            allowed = []
            for av in db_conf_param.allowed_values:
                cpv_kwargs = av.model_dump()
                cpv_kwargs["sort_order"] = cpv_kwargs["sort_order"] or 0
                allowed.append(
                    read_schemas.ConfigurationParameterValueRead(**cpv_kwargs)
                )
            result.append(
                read_schemas.ConfigurationParameterRead(
                    **db_conf_param.model_dump(),
                    allowed_values=allowed,
                )
            )
        return result

    async def delete(self, request: Request, pks: List[Any]) -> Optional[int]:
        for pk in pks:
            conf_param = await anyio.to_thread.run_sync(
                database.get_configuration_parameter, request.state.session, pk
            )
            if conf_param.name in (p.value for p in base.CoreConfParamName):
                raise starlette_admin_exceptions.ActionFailed(
                    f"Cannot delete configuration parameter {conf_param.name!r} - it "
                    f"is a core system parameter"
                )
        else:
            return await super().delete(request, pks)


class CoverageConfigurationView(ModelView):
    identity = "coverage_configurations"
    name = "Coverage Configuration"
    label = "Coverage Configurations"
    icon = "fa fa-blog"
    pk_attr = "id"
    fields = (
        fields.UuidField("id"),
        starlette_admin.StringField("name", required=True),
        starlette_admin.StringField("display_name_english", required=True),
        starlette_admin.StringField("display_name_italian", required=True),
        starlette_admin.StringField("description_english"),
        starlette_admin.StringField("description_italian"),
        starlette_admin.StringField(
            "netcdf_main_dataset_name",
            required=True,
            help_text=(
                "Name of the main variable inside this dataset's NetCDF file. This can "
                "be a templated value, such as '{historical_year_period}_avg'."
            ),
        ),
        starlette_admin.StringField("wms_main_layer_name", required=True),
        starlette_admin.StringField("wms_secondary_layer_name", required=False),
        starlette_admin.StringField(
            "thredds_url_pattern",
            required=True,
            help_text=(
                "Path pattern to the dataset's URL in THREDDS. This can be "
                "templated with the name of any configuration parameter that belongs "
                "to the coverage. This can also be given a shell-like pattern, which "
                "can be useful when the dataset filename differs by additional "
                "characters than just those that are used for configuration parameters. "
                "Example: 'cline_yr/TDd_{historical_year_period}_1992-202[34]_py85.nc' "
                "- this example features the '{historical_year_period}' template, which "
                "gets replaced by the concrete value of the parameter, and it also "
                "features the shell-like style expressed in '202[34]', which means "
                "to look for files that have either '2023' or '2024' in that "
                "part of their name."
            ),
        ),
        starlette_admin.StringField("coverage_id_pattern", disabled=True),
        starlette_admin.StringField("unit_english", required=True),
        starlette_admin.StringField("unit_italian", required=True),
        starlette_admin.StringField(
            "palette",
            required=True,
            help_text=(
                "Name of the palette that should used by the THREDDS WMS server. "
                "Available values can be found at https://reading-escience-centre.gitbooks.io/ncwms-user-guide/content/04-usage.html#getmap"
            ),
        ),
        starlette_admin.FloatField("color_scale_min", required=True),
        starlette_admin.FloatField("color_scale_max", required=True),
        starlette_admin.IntegerField(
            "data_precision",
            required=True,
            help_text=(
                "Number of decimal places to be used when displaying data values"
            ),
        ),
        fields.RelatedObservationsVariableField(
            "observation_variable",
            help_text="Related observation variable",
            choices_loader=related_observation_variable_choices_loader,
        ),
        starlette_admin.EnumField(
            "observation_variable_aggregation_type",
            enum=base.ObservationAggregationType,
        ),
        starlette_admin.ListField(
            field=fields.PossibleConfigurationParameterValuesField(
                "possible_values", choices_loader=possible_values_choices_loader
            )
        ),
        fields.RelatedCoverageconfigurationsField(
            "uncertainty_lower_bounds_coverage_configuration",
            choices_loader=coverage_configurations_choices_loader,
            help_text=(
                "Coverage configuration to be used when looking for coverages "
                "which have the lower uncertainty bounds values"
            ),
        ),
        fields.RelatedCoverageconfigurationsField(
            "uncertainty_upper_bounds_coverage_configuration",
            choices_loader=coverage_configurations_choices_loader,
            help_text=(
                "Coverage configuration to be used when looking for coverages "
                "which have the upper uncertainty bounds values"
            ),
        ),
        starlette_admin.ListField(
            field=fields.RelatedCoverageconfigurationsField(
                "related_coverages",
                choices_loader=coverage_configurations_choices_loader,
                help_text=(
                    "Additional coverages which are related to this one and which "
                    "can be used when requesting time series"
                ),
            )
        ),
    )

    exclude_fields_from_list = (
        "id",
        "display_name_english",
        "display_name_italian",
        "description_english",
        "description_italian",
        "netcdf_main_dataset_name",
        "wms_main_layer_name",
        "wms_secondary_layer_name",
        "coverage_id_pattern",
        "possible_values",
        "unit_english",
        "unit_italian",
        "palette",
        "color_scale_min",
        "color_scale_max",
        "data_precision",
        "observation_variable",
        "observation_variable_aggregation_type",
        "uncertainty_lower_bounds_coverage_configuration",
        "uncertainty_upper_bounds_coverage_configuration",
        "related_coverages",
    )
    exclude_fields_from_edit = ("coverage_id_pattern",)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon = "fa-solid fa-map"

    async def get_pk_value(self, request: Request, obj: Any) -> Any:
        # note: we need to cast the value, which is a uuid.UUID, to a string
        # because starlette_admin just assumes that the value of a model's
        # pk attribute is always JSON serializable so it doesn't bother with
        # calling the respective field's `serialize_value()` method
        result = await super().get_pk_value(request, obj)
        return str(result)

    @staticmethod
    def _serialize_instance(instance: coverages.CoverageConfiguration):
        obs_variable = instance.related_observation_variable
        if obs_variable is not None:
            observation_variable = read_schemas.ObservationVariableRead(
                **obs_variable.model_dump()
            )
        else:
            observation_variable = None
        uncertainty_lower_cov_conf = (
            instance.uncertainty_lower_bounds_coverage_configuration
        )
        if uncertainty_lower_cov_conf is not None:
            uncertainty_lower_bounds_coverage_configuration = (
                read_schemas.CoverageConfigurationReadListItem(
                    id=uncertainty_lower_cov_conf.id,
                    name=uncertainty_lower_cov_conf.name,
                )
            )
        else:
            uncertainty_lower_bounds_coverage_configuration = None
        uncertainty_upper_cov_conf = (
            instance.uncertainty_upper_bounds_coverage_configuration
        )
        if uncertainty_upper_cov_conf is not None:
            uncertainty_upper_bounds_coverage_configuration = (
                read_schemas.CoverageConfigurationReadListItem(
                    id=uncertainty_upper_cov_conf.id,
                    name=uncertainty_upper_cov_conf.name,
                )
            )
        else:
            uncertainty_upper_bounds_coverage_configuration = None
        return read_schemas.CoverageConfigurationRead(
            **instance.model_dump(exclude={"observation_variable_aggregation_type"}),
            observation_variable_aggregation_type=(
                instance.observation_variable_aggregation_type
                or base.ObservationAggregationType.SEASONAL
            ),
            observation_variable=observation_variable,
            possible_values=[
                read_schemas.ConfigurationParameterPossibleValueRead(
                    configuration_parameter_value_id=pv.configuration_parameter_value_id,
                    configuration_parameter_value_name=pv.configuration_parameter_value.name,
                )
                for pv in instance.possible_values
            ],
            uncertainty_lower_bounds_coverage_configuration=uncertainty_lower_bounds_coverage_configuration,
            uncertainty_upper_bounds_coverage_configuration=uncertainty_upper_bounds_coverage_configuration,
            related_coverages=[
                read_schemas.RelatedCoverageConfigurationRead(
                    id=rcc.secondary_coverage_configuration_id,
                    name=rcc.secondary_coverage_configuration.name,
                )
                for rcc in instance.secondary_coverage_configurations
            ],
        )

    async def find_by_pk(
        self, request: Request, pk: Any
    ) -> read_schemas.CoverageConfigurationRead:
        db_cov_conf = await anyio.to_thread.run_sync(
            database.get_coverage_configuration, request.state.session, pk
        )
        return self._serialize_instance(db_cov_conf)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[Dict[str, Any], str, None] = None,
        order_by: Optional[List[str]] = None,
    ) -> Sequence[read_schemas.CoverageConfigurationRead]:
        list_cov_confs = functools.partial(
            database.list_coverage_configurations,
            limit=limit,
            offset=skip,
            name_filter=str(where) if where not in (None, "") else None,
            include_total=False,
        )
        db_cov_confs, _ = await anyio.to_thread.run_sync(
            list_cov_confs, request.state.session
        )
        result = []
        for db_cov_conf in db_cov_confs:
            result.append(self._serialize_instance(db_cov_conf))
        return result

    async def create(self, request: Request, data: Dict[str, Any]) -> Any:
        session = request.state.session
        try:
            data = await self._arrange_data(request, data)
            await self.validate(request, data)
            logger.debug(f"{data=}")
            possible_values_create = []
            for possible_value in data["possible_values"]:
                param_name, param_value = possible_value.partition(" - ")[::2]
                conf_param = database.get_configuration_parameter_by_name(
                    session, param_name
                )
                conf_param_value = [
                    pv for pv in conf_param.allowed_values if pv.name == param_value
                ][0]
                possible_values_create.append(
                    coverages.ConfigurationParameterPossibleValueCreate(
                        configuration_parameter_value_id=conf_param_value.id
                    )
                )
            related_obs_variable = database.get_variable_by_name(
                session, data["observation_variable"]
            )
            if (
                uncertainty_lower_name := data.get(
                    "uncertainty_lower_bounds_coverage_configuration"
                )
            ) is not None:
                db_uncertainty_lower = database.get_coverage_configuration_by_name(
                    session, uncertainty_lower_name
                )
                uncertainty_lower_id = db_uncertainty_lower.id
            else:
                uncertainty_lower_id = None
            if (
                uncertainty_upper_name := data.get(
                    "uncertainty_upper_bounds_coverage_configuration"
                )
            ) is not None:
                db_uncertainty_upper = database.get_coverage_configuration_by_name(
                    session, uncertainty_upper_name
                )
                uncertainty_upper_id = db_uncertainty_upper.id
            else:
                uncertainty_upper_id = None
            related_cov_conf_ids = []
            for related_cov_conf_name in data.get("related_coverages", []):
                db_related_cov_conf = database.get_coverage_configuration_by_name(
                    session, related_cov_conf_name
                )
                related_cov_conf_ids.append(db_related_cov_conf.id)
            cov_conf_create = coverages.CoverageConfigurationCreate(
                name=data["name"],
                display_name_english=data["display_name_english"],
                display_name_italian=data["display_name_italian"],
                description_english=data.get("display_name_english"),
                description_italian=data.get("display_name_italian"),
                netcdf_main_dataset_name=data["netcdf_main_dataset_name"],
                wms_main_layer_name=data.get("wms_main_layer_name"),
                wms_secondary_layer_name=data.get("wms_secondary_layer_name"),
                thredds_url_pattern=data["thredds_url_pattern"],
                unit_english=data["unit_english"],
                unit_italian=data["unit_italian"],
                palette=data["palette"],
                color_scale_min=data["color_scale_min"],
                color_scale_max=data["color_scale_max"],
                data_precision=data["data_precision"],
                possible_values=possible_values_create,
                observation_variable_id=(
                    related_obs_variable.id if related_obs_variable else None
                ),
                observation_variable_aggregation_type=data.get(
                    "observation_variable_aggregation_type"
                ),
                uncertainty_lower_bounds_coverage_configuration_id=uncertainty_lower_id,
                uncertainty_upper_bounds_coverage_configuration_id=uncertainty_upper_id,
                secondary_coverage_configurations_ids=related_cov_conf_ids,
            )
            db_cov_conf = await anyio.to_thread.run_sync(
                database.create_coverage_configuration, session, cov_conf_create
            )
            return self._serialize_instance(db_cov_conf)
        except Exception as e:
            return self.handle_exception(e)

    async def edit(self, request: Request, pk: Any, data: Dict[str, Any]) -> Any:
        session = request.state.session
        try:
            data = await self._arrange_data(request, data, True)
            await self.validate(request, data)

            possible_values = []
            for pv in data["possible_values"]:
                param_name, param_value = pv.rpartition(" - ")[::2]
                conf_param = database.get_configuration_parameter_by_name(
                    session, param_name
                )
                conf_param_value = [
                    pv for pv in conf_param.allowed_values if pv.name == param_value
                ][0]
                possible_values.append(
                    coverages.ConfigurationParameterPossibleValueUpdate(
                        configuration_parameter_value_id=conf_param_value.id
                    )
                )
            related_obs_variable = database.get_variable_by_name(
                session, data["observation_variable"]
            )
            if (
                uncertainty_lower_name := data.get(
                    "uncertainty_lower_bounds_coverage_configuration"
                )
            ) is not None:
                db_uncertainty_lower = database.get_coverage_configuration_by_name(
                    session, uncertainty_lower_name
                )
                uncertainty_lower_id = db_uncertainty_lower.id
            else:
                uncertainty_lower_id = None
            if (
                uncertainty_upper_name := data.get(
                    "uncertainty_upper_bounds_coverage_configuration"
                )
            ) is not None:
                db_uncertainty_upper = database.get_coverage_configuration_by_name(
                    session, uncertainty_upper_name
                )
                uncertainty_upper_id = db_uncertainty_upper.id
            else:
                uncertainty_upper_id = None
            related_cov_conf_ids = []
            for related_cov_conf_name in data.get("related_coverages", []):
                db_related_cov_conf = database.get_coverage_configuration_by_name(
                    session, related_cov_conf_name
                )
                related_cov_conf_ids.append(db_related_cov_conf.id)
            cov_conv_update = coverages.CoverageConfigurationUpdate(
                name=data.get("name"),
                display_name_english=data.get("display_name_english"),
                display_name_italian=data.get("display_name_italian"),
                description_english=data.get("display_name_english"),
                description_italian=data.get("display_name_italian"),
                netcdf_main_dataset_name=data.get("netcdf_main_dataset_name"),
                wms_main_layer_name=data.get("wms_main_layer_name"),
                wms_secondary_layer_name=data.get("wms_secondary_layer_name"),
                thredds_url_pattern=data.get("thredds_url_pattern"),
                unit_english=data.get("unit_english"),
                unit_italian=data.get("unit_italian"),
                palette=data.get("palette"),
                color_scale_min=data.get("color_scale_min"),
                color_scale_max=data.get("color_scale_max"),
                data_precision=data.get("data_precision"),
                possible_values=possible_values,
                observation_variable_id=(
                    related_obs_variable.id if related_obs_variable else None
                ),
                observation_variable_aggregation_type=data.get(
                    "observation_variable_aggregation_type"
                ),
                uncertainty_lower_bounds_coverage_configuration_id=uncertainty_lower_id,
                uncertainty_upper_bounds_coverage_configuration_id=uncertainty_upper_id,
                secondary_coverage_configurations_ids=related_cov_conf_ids,
            )
            db_coverage_configuration = await anyio.to_thread.run_sync(
                database.get_coverage_configuration, session, pk
            )
            db_coverage_configuration = await anyio.to_thread.run_sync(
                database.update_coverage_configuration,
                session,
                db_coverage_configuration,
                cov_conv_update,
            )
            return self._serialize_instance(db_coverage_configuration)
        except Exception as e:
            self.handle_exception(e)
