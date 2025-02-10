import functools
import logging
from typing import (
    Any,
    Optional,
    Sequence,
    Union,
)

import anyio
from geoalchemy2.shape import from_shape
import geojson_pydantic
import shapely.io
import starlette_admin
from starlette.requests import Request
from starlette_admin.contrib.sqlmodel import ModelView
from starlette_admin.exceptions import FormValidationError

from .... import database as db
from ....schemas import (
    base,
    observations,
)
from .. import fields
from .. import schemas as read_schemas

logger = logging.getLogger(__name__)


class MonthlyMeasurementView(ModelView):
    identity = "monthly measurements"
    name = "Monthly Measurements"
    label = "Monthly Measurements"
    pk_attr = "id"

    fields = (
        starlette_admin.StringField("station", required=True),
        starlette_admin.StringField("variable", required=True),
        starlette_admin.DateField("date", required=True),
        starlette_admin.FloatField("value", required=True),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon = "fa-regular fa-calendar-days"

    def can_create(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False

    def can_view_details(self, request: Request) -> bool:
        return False

    @staticmethod
    def _serialize_instance(
        instance: observations.MonthlyMeasurement,
    ) -> read_schemas.MonthlyMeasurementRead:
        return read_schemas.MonthlyMeasurementRead(
            **instance.model_dump(),
            station=instance.station.code,
            variable=instance.variable.name,
        )

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[read_schemas.MonthlyMeasurementRead]:
        list_measurements = functools.partial(
            db.list_monthly_measurements,
            limit=limit,
            offset=skip,
            include_total=False,
        )
        db_measurements, _ = await anyio.to_thread.run_sync(
            list_measurements, request.state.session
        )
        return [self._serialize_instance(item) for item in db_measurements]


class SeasonalMeasurementView(ModelView):
    identity = "seasonal measurements"
    name = "Seasonal Measurements"
    label = "Seasonal Measurements"
    icon = "fa fa-blog"
    pk_attr = "id"

    fields = (
        starlette_admin.StringField("station", required=True),
        starlette_admin.StringField("variable", required=True),
        starlette_admin.IntegerField("year", required=True),
        starlette_admin.EnumField("season", enum=base.Season, required=True),
        starlette_admin.FloatField("value", required=True),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon = "fa-regular fa-calendar-days"

    def can_create(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False

    def can_view_details(self, request: Request) -> bool:
        return False

    @staticmethod
    def _serialize_instance(
        instance: observations.SeasonalMeasurement,
    ) -> read_schemas.SeasonalMeasurementRead:
        return read_schemas.SeasonalMeasurementRead(
            **instance.model_dump(),
            station=instance.station.code,
            variable=instance.variable.name,
        )

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[read_schemas.SeasonalMeasurementRead]:
        list_measurements = functools.partial(
            db.list_seasonal_measurements,
            limit=limit,
            offset=skip,
            include_total=False,
        )
        db_measurements, _ = await anyio.to_thread.run_sync(
            list_measurements, request.state.session
        )
        return [self._serialize_instance(item) for item in db_measurements]


class YearlyMeasurementView(ModelView):
    identity = "yearly measurements"
    name = "Yearly Measurements"
    label = "Yearly Measurements"
    icon = "fa fa-blog"
    pk_attr = "id"

    fields = (
        starlette_admin.StringField("station", required=True),
        starlette_admin.StringField("variable", required=True),
        starlette_admin.IntegerField("year", required=True),
        starlette_admin.FloatField("value", required=True),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon = "fa-regular fa-calendar-days"

    def can_create(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False

    def can_view_details(self, request: Request) -> bool:
        return False

    @staticmethod
    def _serialize_instance(
        instance: observations.YearlyMeasurement,
    ) -> read_schemas.YearlyMeasurementRead:
        return read_schemas.YearlyMeasurementRead(
            **instance.model_dump(),
            station=instance.station.code,
            variable=instance.variable.name,
        )

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[read_schemas.YearlyMeasurementRead]:
        list_measurements = functools.partial(
            db.list_yearly_measurements,
            limit=limit,
            offset=skip,
            include_total=False,
        )
        db_measurements, _ = await anyio.to_thread.run_sync(
            list_measurements, request.state.session
        )
        return [self._serialize_instance(item) for item in db_measurements]


class VariableView(ModelView):
    identity = "variables"
    name = "Variable"
    label = "Variables"
    icon = "fa fa-blog"
    pk_attr = "id"

    exclude_fields_from_list = (
        "id",
        "display_name_english",
        "display_name_italian",
        "description_english",
        "description_italian",
        "unit_english",
        "unit_italian",
    )
    exclude_fields_from_detail = ("id",)

    fields = (
        fields.UuidField("id"),
        starlette_admin.StringField("name", required=True),
        starlette_admin.StringField("display_name_english", required=True),
        starlette_admin.StringField("display_name_italian", required=True),
        starlette_admin.StringField("description_english"),
        starlette_admin.StringField("description_italian"),
        starlette_admin.StringField("unit_english"),
        starlette_admin.StringField("unit_italian"),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon = "fa-solid fa-cloud-sun-rain"

    @staticmethod
    def _serialize_instance(
        instance: observations.Variable,
    ) -> read_schemas.VariableRead:
        return read_schemas.VariableRead(**instance.model_dump())

    async def get_pk_value(self, request: Request, obj: Any) -> str:
        # note: we need to cast the value, which is a uuid.UUID, to a string
        # because starlette_admin just assumes that the value of a model's
        # pk attribute is always JSON serializable so it doesn't bother with
        # calling the respective field's `serialize_value()` method
        result = await super().get_pk_value(request, obj)
        return str(result)

    async def create(
        self, request: Request, data: dict[str, Any]
    ) -> Optional[read_schemas.VariableRead]:
        try:
            data = await self._arrange_data(request, data)
            await self.validate(request, data)
            var_create = observations.VariableCreate(**data)
            db_variable = await anyio.to_thread.run_sync(
                db.create_variable,
                request.state.session,
                var_create,
            )
            return self._serialize_instance(db_variable)
        except Exception as e:
            return self.handle_exception(e)

    async def edit(
        self, request: Request, pk: Any, data: dict[str, Any]
    ) -> Optional[read_schemas.VariableRead]:
        try:
            data = await self._arrange_data(request, data, True)
            await self.validate(request, data)
            var_update = observations.VariableUpdate(**data)
            db_var = await anyio.to_thread.run_sync(
                db.get_variable, request.state.session, pk
            )
            db_var = await anyio.to_thread.run_sync(
                db.update_variable, request.state.session, db_var, var_update
            )
            return self._serialize_instance(db_var)
        except Exception as e:
            logger.exception("something went wrong")
            self.handle_exception(e)

    async def find_by_pk(self, request: Request, pk: Any) -> read_schemas.VariableRead:
        db_var = await anyio.to_thread.run_sync(
            db.get_variable, request.state.session, pk
        )
        return self._serialize_instance(db_var)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[read_schemas.VariableRead]:
        list_variables = functools.partial(
            db.list_variables,
            limit=limit,
            offset=skip,
            name_filter=str(where) if where not in (None, "") else None,
            include_total=False,
        )
        db_vars, _ = await anyio.to_thread.run_sync(
            list_variables, request.state.session
        )
        return [self._serialize_instance(db_var) for db_var in db_vars]


class StationView(ModelView):
    identity = "stations"
    name = "Station"
    label = "Stations"
    icon = "fa fa-blog"
    pk_attr = "id"

    exclude_fields_from_list = ("id",)
    exclude_fields_from_detail = ("id",)

    fields = (
        fields.UuidField("id"),
        starlette_admin.StringField("name", required=True),
        starlette_admin.StringField("code", required=True),
        starlette_admin.StringField("type_", required=True),
        starlette_admin.FloatField("longitude", required=True),
        starlette_admin.FloatField("latitude", required=True),
        starlette_admin.DateField("active_since"),
        starlette_admin.DateField("active_until"),
        starlette_admin.FloatField("altitude_m"),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon = "fa-solid fa-tower-observation"

    @staticmethod
    def _serialize_instance(instance: observations.Station) -> read_schemas.StationRead:
        geom = shapely.io.from_wkb(bytes(instance.geom.data))
        return read_schemas.StationRead(
            **instance.model_dump(exclude={"geom", "type_"}),
            type=instance.type_,
            longitude=geom.x,
            latitude=geom.y,
        )

    async def get_pk_value(self, request: Request, obj: Any) -> str:
        # note: we need to cast the value, which is a uuid.UUID, to a string
        # because starlette_admin just assumes that the value of a model's
        # pk attribute is always JSON serializable so it doesn't bother with
        # calling the respective field's `serialize_value()` method
        result = await super().get_pk_value(request, obj)
        return str(result)

    async def validate(self, request: Request, data: dict[str, Any]) -> None:
        """Validate data without file fields  relation fields"""
        errors: dict[str, str] = {}
        if (lat := data["latitude"]) < -90 or lat > 90:
            errors["latitude"] = "Invalid value"
        if (lon := data["longitude"]) < -180 or lon > 180:
            errors["longitude"] = "Invalid longitude"
        if len(errors) > 0:
            raise FormValidationError(errors)
        else:
            data_to_validate = data.copy()
            data_to_validate["geom"] = from_shape(shapely.Point(lon, lat))
            del data_to_validate["longitude"]
            del data_to_validate["latitude"]
            fields_to_exclude = [
                f.name
                for f in self.get_fields_list(request, request.state.action)
                if isinstance(
                    f, (starlette_admin.FileField, starlette_admin.RelationField)
                )
            ] + ["latitude", "longitude"]
            self.model.validate(
                {
                    k: v
                    for k, v in data_to_validate.items()
                    if k not in fields_to_exclude
                }
            )

    async def create(
        self, request: Request, data: dict[str, Any]
    ) -> Optional[read_schemas.StationRead]:
        try:
            data = await self._arrange_data(request, data)
            await self.validate(request, data)
            geojson_geom = geojson_pydantic.Point(
                type="Point", coordinates=(data.pop("longitude"), data.pop("latitude"))
            )
            station_create = observations.StationCreate(
                type_=data.pop("type"),
                geom=geojson_geom,
                **data,
            )
            db_station = await anyio.to_thread.run_sync(
                db.create_station,
                request.state.session,
                station_create,
            )
            return self._serialize_instance(db_station)
        except Exception as e:
            logger.exception("could not create")
            return self.handle_exception(e)

    async def edit(
        self, request: Request, pk: Any, data: dict[str, Any]
    ) -> Optional[read_schemas.StationRead]:
        try:
            data = await self._arrange_data(request, data, True)
            await self.validate(request, data)
            lon = data.pop("longitude", None)
            lat = data.pop("latitude", None)
            kwargs = {}
            if all((lon, lat)):
                kwargs["geom"] = geojson_pydantic.Point(
                    type="Point", coordinates=(lon, lat)
                )
            if (type_ := data.pop("type", None)) is not None:
                kwargs["type_"] = type_
            station_update = observations.StationUpdate(**data, **kwargs)
            db_station = await anyio.to_thread.run_sync(
                db.get_station, request.state.session, pk
            )
            db_station = await anyio.to_thread.run_sync(
                db.update_station, request.state.session, db_station, station_update
            )
            return self._serialize_instance(db_station)
        except Exception as e:
            logger.exception("something went wrong")
            self.handle_exception(e)

    async def find_by_pk(self, request: Request, pk: Any) -> read_schemas.StationRead:
        db_station = await anyio.to_thread.run_sync(
            db.get_station, request.state.session, pk
        )
        return self._serialize_instance(db_station)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[read_schemas.StationRead]:
        list_stations = functools.partial(
            db.list_stations,
            limit=limit,
            offset=skip,
            include_total=False,
            name_filter=str(where) if where not in (None, "") else None,
        )
        db_stations, _ = await anyio.to_thread.run_sync(
            list_stations, request.state.session
        )
        return [self._serialize_instance(db_station) for db_station in db_stations]
