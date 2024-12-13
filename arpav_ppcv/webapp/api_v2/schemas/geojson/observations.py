from fastapi import Request
import geojson_pydantic
import pydantic

from .....schemas import (
    observations,
    fields,
)
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
        instance: observations.ObservationStation,
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
            },
            links=[str(url)],
        )


class StationFeatureCollection(ArpavFeatureCollection):
    path_operation_name = "list_stations"
    list_item_type = StationFeatureCollectionItem
