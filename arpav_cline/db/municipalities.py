from typing import (
    Optional,
    Sequence,
)

import geojson_pydantic
import shapely
import sqlalchemy
import sqlmodel
from geoalchemy2.shape import from_shape
from sqlalchemy import func

from ..schemas.municipalities import (
    Municipality,
    MunicipalityCentroid,
    MunicipalityCreate,
)

from .base import (
    add_substring_filter,
    get_total_num_records,
)


def list_municipality_centroids(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    polygon_intersection_filter: shapely.Polygon = None,
    name_filter: Optional[str] = None,
    province_name_filter: Optional[str] = None,
    region_name_filter: Optional[str] = None,
) -> tuple[Sequence[MunicipalityCentroid], Optional[int]]:
    """List existing municipality centroids.

    ``polygon_intersection_filter`` parameter is expected to be express a geometry in
    the EPSG:4326 CRS.
    """
    statement = sqlmodel.select(Municipality).order_by(Municipality.name)  # noqa
    if name_filter is not None:
        statement = add_substring_filter(
            statement,
            name_filter,
            Municipality.name,  # noqa
        )
    if province_name_filter is not None:
        statement = add_substring_filter(
            statement,
            province_name_filter,
            Municipality.province_name,  # noqa
        )
    if region_name_filter is not None:
        statement = add_substring_filter(
            statement,
            region_name_filter,
            Municipality.region_name,  # noqa
        )
    if polygon_intersection_filter is not None:
        statement = statement.where(
            func.ST_Intersects(
                Municipality.geom,  # noqa
                func.ST_GeomFromWKB(
                    shapely.io.to_wkb(polygon_intersection_filter), 4326
                ),
            )
        )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return [
        MunicipalityCentroid(
            id=i.id,
            name=i.name,
            province_name=i.province_name,
            region_name=i.region_name,
            geom=geojson_pydantic.Point(
                type="Point",
                coordinates=(i.centroid_epsg_4326_lon, i.centroid_epsg_4326_lat),
            ),
        )
        for i in items
    ], num_items


def list_municipalities(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    polygon_intersection_filter: shapely.Polygon = None,
    point_filter: shapely.Point = None,
    name_filter: Optional[str] = None,
    province_name_filter: Optional[str] = None,
    region_name_filter: Optional[str] = None,
) -> tuple[Sequence[Municipality], Optional[int]]:
    """List existing municipalities.

    Both ``polygon_intersection_filter`` and ``point_filter`` parameters are expected
    to be a geometries in the EPSG:4326 CRS.
    """
    statement = sqlmodel.select(Municipality).order_by(
        Municipality.name  # noqa
    )
    if name_filter is not None:
        statement = add_substring_filter(
            statement,
            name_filter,
            Municipality.name,  # noqa
        )
    if province_name_filter is not None:
        statement = add_substring_filter(
            statement,
            province_name_filter,
            Municipality.province_name,  # noqa
        )
    if region_name_filter is not None:
        statement = add_substring_filter(
            statement,
            region_name_filter,
            Municipality.region_name,  # noqa
        )
    if polygon_intersection_filter is not None:
        statement = statement.where(
            func.ST_Intersects(
                Municipality.geom,  # noqa
                func.ST_GeomFromWKB(
                    shapely.io.to_wkb(polygon_intersection_filter), 4326
                ),
            )
        )
    if point_filter is not None:
        statement = statement.where(
            func.ST_Intersects(
                Municipality.geom,  # noqa
                func.ST_GeomFromWKB(shapely.io.to_wkb(point_filter), 4326),
            )
        )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_municipalities(
    session: sqlmodel.Session,
) -> Sequence[Municipality]:
    _, num_total = list_municipalities(session, limit=1, include_total=True)
    result, _ = list_municipalities(session, limit=num_total, include_total=False)
    return result


def create_many_municipalities(
    session: sqlmodel.Session,
    municipalities_to_create: Sequence[MunicipalityCreate],
) -> list[Municipality]:
    """Create several municipalities."""
    db_records = []
    for mun_create in municipalities_to_create:
        geom = shapely.io.from_geojson(mun_create.geom.model_dump_json())
        wkbelement = from_shape(geom)
        db_mun = Municipality(
            **mun_create.model_dump(exclude={"geom"}),
            geom=wkbelement,
        )
        db_records.append(db_mun)
        session.add(db_mun)
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        for db_record in db_records:
            session.refresh(db_record)
        return db_records


def delete_all_municipalities(session: sqlmodel.Session) -> None:
    """Delete all municipalities."""
    for db_municipality in collect_all_municipalities(session):
        session.delete(db_municipality)
    session.commit()
