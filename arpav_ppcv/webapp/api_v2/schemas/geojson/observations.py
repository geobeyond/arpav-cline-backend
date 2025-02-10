from fastapi import Request
import geojson_pydantic
import pydantic

from .....schemas import (
    observations,
    fields,
)
from ..observations import VariableReadEmbeddedInStationRead
from .base import ArpavFeatureCollection


class StationFeatureCollectionItem(geojson_pydantic.Feature):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    type: str = "Feature"
    id: pydantic.UUID4
    geometry: fields.WkbElement
    links: list[str]

    @classmethod
    def from_db_instance(
        cls,
        instance: observations.Station,
        request: Request,
    ) -> "StationFeatureCollectionItem":
        url = request.url_for("get_station", **{"station_id": instance.id})
        return cls(
            id=instance.id,
            geometry=instance.geom,
            properties={
                **instance.model_dump(
                    exclude={
                        "id",
                        "geom",
                    }
                ),
                "monthly_variables": [
                    VariableReadEmbeddedInStationRead(**v.model_dump())
                    for v in instance.monthly_variables
                ],
                "seasonal_variables": [
                    VariableReadEmbeddedInStationRead(**v.model_dump())
                    for v in instance.seasonal_variables
                ],
                "yearly_variables": [
                    VariableReadEmbeddedInStationRead(**v.model_dump())
                    for v in instance.yearly_variables
                ],
            },
            links=[str(url)],
        )


class StationFeatureCollection(ArpavFeatureCollection):
    path_operation_name = "list_stations"
    list_item_type = StationFeatureCollectionItem
