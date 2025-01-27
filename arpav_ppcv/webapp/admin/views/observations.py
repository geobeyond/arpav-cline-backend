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
import shapely.io
import starlette_admin
from starlette.requests import Request
from starlette_admin.contrib.sqlmodel import ModelView
from starlette_admin.exceptions import FormValidationError

from .... import database
from ....schemas import (
    observations,
    static,
)
from .. import fields
from .. import schemas as read_schemas

logger = logging.getLogger(__name__)


class ObservationMeasurementView(ModelView):
    identity = "observation measurements"
    name = "Observation Measurements"
    label = "Measurements"
    pk_attr = "id"

    fields = (
        fields.RelatedObservationStationField("observation_station", required=True),
        fields.RelatedClimaticIndicatorField("climatic_indicator", required=True),
        starlette_admin.EnumField(
            "measurement_aggregation_type",
            enum=static.MeasurementAggregationType,
            required=True,
        ),
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
        instance: observations.ObservationMeasurement,
    ) -> read_schemas.ObservationMeasurementRead:
        return read_schemas.ObservationMeasurementRead(
            **instance.model_dump(
                exclude={"observation_station", "climatic_indicator"}
            ),
            observation_station=instance.observation_station_id,
            climatic_indicator=instance.climatic_indicator_id,
        )

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[read_schemas.ObservationMeasurementRead]:
        list_measurements = functools.partial(
            database.list_observation_measurements,
            limit=limit,
            offset=skip,
            include_total=False,
        )
        db_measurements, _ = await anyio.to_thread.run_sync(
            list_measurements, request.state.session
        )
        return [self._serialize_instance(item) for item in db_measurements]


class ObservationStationView(ModelView):
    identity = "observation_stations"
    name = "Observation Station"
    label = "Stations"
    icon = "fa fa-blog"
    pk_attr = "id"

    exclude_fields_from_list = ("id",)
    exclude_fields_from_detail = ("id",)

    fields = (
        fields.UuidField("id"),
        starlette_admin.StringField("name", required=True),
        starlette_admin.EnumField(
            "managed_by", enum=static.ObservationStationManager, required=True
        ),
        starlette_admin.StringField("code", required=True),
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
    def _serialize_instance(
        instance: observations.ObservationStation,
    ) -> read_schemas.ObservationStationRead:
        geom = shapely.io.from_wkb(bytes(instance.geom.data))
        return read_schemas.ObservationStationRead(
            **instance.model_dump(exclude={"geom", "type_"}),
            longitude=geom.x,
            latitude=geom.y,
        )

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

    def can_create(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False

    async def find_by_pk(
        self, request: Request, pk: Any
    ) -> read_schemas.ObservationStationRead:
        db_station = await anyio.to_thread.run_sync(
            database.get_observation_station, request.state.session, pk
        )
        return self._serialize_instance(db_station)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[read_schemas.ObservationStationRead]:
        list_observation_stations = functools.partial(
            database.list_observation_stations,
            limit=limit,
            offset=skip,
            include_total=False,
            name_filter=str(where) if where not in (None, "") else None,
        )
        db_stations, _ = await anyio.to_thread.run_sync(
            list_observation_stations, request.state.session
        )
        return [self._serialize_instance(db_station) for db_station in db_stations]


class ObservationSeriesConfigurationView(ModelView):
    identity = "observation_series_configurations"
    name = "Observation Series Configuration"
    label = "Series Configurations"
    icon = "fa fa-blog"
    pk_attr = "id"
    fields = (
        starlette_admin.IntegerField("id"),
        starlette_admin.StringField("identifier", read_only=True),
        starlette_admin.EnumField(
            "measurement_aggregation_type",
            enum=static.MeasurementAggregationType,
            required=True,
        ),
        fields.RelatedClimaticIndicatorField(
            "climatic_indicator",
            help_text="Related climatic indicator",
            required=True,
        ),
        starlette_admin.ListField(
            starlette_admin.EnumField(
                "station_managers", enum=static.ObservationStationManager
            )
        ),
    )

    exclude_fields_from_list = (
        "id",
        "measurement_aggregation_type",
        "climatic_indicator",
        "station_owners",
    )
    exclude_fields_from_detail = ("id",)
    exclude_fields_from_edit = (
        "id",
        "identifier",
    )
    exclude_fields_from_create = ("identifier",)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon = "fa-solid fa-map"

    @staticmethod
    def _serialize_instance(
        instance: observations.ObservationSeriesConfiguration,
    ) -> read_schemas.ObservationSeriesConfigurationRead:
        return read_schemas.ObservationSeriesConfigurationRead(
            **instance.model_dump(
                exclude={
                    "climatic_indicator_id",
                },
            ),
            climatic_indicator=instance.climatic_indicator_id,
        )

    async def find_by_pk(
        self, request: Request, pk: Any
    ) -> read_schemas.ObservationSeriesConfigurationRead:
        db_instance = await anyio.to_thread.run_sync(
            database.get_observation_series_configuration, request.state.session, pk
        )
        return self._serialize_instance(db_instance)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[dict[str, Any], str, None] = None,
        order_by: Optional[list[str]] = None,
    ) -> Sequence[read_schemas.ObservationSeriesConfigurationRead]:
        item_lister = functools.partial(
            database.list_observation_series_configurations,
            limit=limit,
            offset=skip,
            include_total=False,
        )
        db_items, _ = await anyio.to_thread.run_sync(item_lister, request.state.session)
        result = []
        for db_item in db_items:
            result.append(self._serialize_instance(db_item))
        return result

    async def create(self, request: Request, data: dict[str, Any]) -> Any:
        session = request.state.session
        try:
            data = await self._arrange_data(request, data)
            await self.validate(request, data)
            logger.debug(f"{data=}")
            # FIXME: looks like this needs to be called with anyio.to_thread.run_sync
            climatic_indicator = await anyio.to_thread.run_sync(
                database.get_climatic_indicator,
                session,
                data["climatic_indicator"],
            )
            item_create = observations.ObservationSeriesConfigurationCreate(
                climatic_indicator_id=climatic_indicator.id,
                indicator_internal_name=data["indicator_internal_name"],
                measurement_aggregation_type=data["measurement_aggregation_type"],
                station_owners=data["station_owners"],
            )
            db_item = await anyio.to_thread.run_sync(
                database.create_observation_series_configuration, session, item_create
            )
            return self._serialize_instance(db_item)
        except Exception as e:
            return self.handle_exception(e)

    async def edit(self, request: Request, pk: Any, data: dict[str, Any]) -> Any:
        session = request.state.session
        try:
            data = await self._arrange_data(request, data, True)
            await self.validate(request, data)

            # FIXME: call this via anyio.to_thread.run_sync
            climatic_indicator = await anyio.to_thread.run_sync(
                database.get_climatic_indicator, session, data["climatic_indicator"]
            )
            item_update = observations.ObservationSeriesConfigurationUpdate(
                climatic_indicator_id=climatic_indicator.id,
                indicator_internal_name=data["indicator_internal_name"],
                measurement_aggregation_type=data["measurement_aggregation_type"],
                station_owners=data["station_owners"],
            )
            db_item = await anyio.to_thread.run_sync(
                database.get_observation_series_configuration, session, pk
            )
            db_item = await anyio.to_thread.run_sync(
                database.update_observation_series_configuration,
                session,
                db_item,
                item_update,
            )
            return self._serialize_instance(db_item)
        except Exception as e:
            self.handle_exception(e)
