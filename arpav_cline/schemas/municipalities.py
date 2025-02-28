import uuid

import geoalchemy2
import geojson_pydantic
import pydantic
import sqlalchemy
import sqlmodel

from . import fields


class Municipality(sqlmodel.SQLModel, table=True):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    id: pydantic.UUID4 = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True)
    geom: fields.WkbElement = sqlmodel.Field(
        sa_column=sqlalchemy.Column(
            geoalchemy2.Geometry(
                srid=4326,
                geometry_type="MULTIPOLYGON",
                spatial_index=True,
            )
        )
    )
    name: str
    province_name: str
    region_name: str
    centroid_epsg_4326_lon: float | None = None
    centroid_epsg_4326_lat: float | None = None


class MunicipalityCreate(sqlmodel.SQLModel):
    geom: geojson_pydantic.MultiPolygon
    name: str
    province_name: str
    region_name: str
    centroid_epsg_4326_lon: float | None = None
    centroid_epsg_4326_lat: float | None = None


class MunicipalityCentroid(sqlmodel.SQLModel):
    # model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    id: pydantic.UUID4
    geom: geojson_pydantic.Point
    name: str
    province_name: str
    region_name: str
