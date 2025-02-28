from typing import (
    Optional,
    Sequence,
)

import shapely.io
import sqlalchemy
import sqlmodel
from geoalchemy2.shape import from_shape

from ..schemas.base import (
    SpatialRegion,
    SpatialRegionCreate,
    SpatialRegionUpdate,
)

from .base import get_total_num_records


def list_spatial_regions(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
) -> tuple[Sequence[SpatialRegion], Optional[int]]:
    statement = sqlmodel.select(SpatialRegion).order_by(SpatialRegion.name)  # noqa
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_spatial_regions(
    session: sqlmodel.Session,
) -> Sequence[SpatialRegion]:
    _, num_total = list_spatial_regions(
        session,
        limit=1,
        include_total=True,
    )
    result, _ = list_spatial_regions(
        session,
        limit=num_total,
        include_total=False,
    )
    return result


def get_spatial_region(
    session: sqlmodel.Session, spatial_region_id: int
) -> Optional[SpatialRegion]:
    return session.get(SpatialRegion, spatial_region_id)


def get_spatial_region_by_name(
    session: sqlmodel.Session, name: str
) -> Optional[SpatialRegion]:
    """Get a spatial region by its name."""
    return session.exec(
        sqlmodel.select(SpatialRegion).where(SpatialRegion.name == name)  # noqa
    ).first()


def create_spatial_region(
    session: sqlmodel.Session,
    spatial_region_create: SpatialRegionCreate,
):
    """Create a new spatial region."""
    geom = shapely.io.from_geojson(spatial_region_create.geom.model_dump_json())
    wkbelement = from_shape(geom)
    db_item = SpatialRegion(
        **spatial_region_create.model_dump(exclude={"geom"}),
        geom=wkbelement,
    )
    session.add(db_item)
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        session.refresh(db_item)
        return db_item


def update_spatial_region(
    session: sqlmodel.Session,
    db_spatial_region: SpatialRegion,
    spatial_region_update: SpatialRegionUpdate,
) -> SpatialRegion:
    """Update a spatial region."""
    geom = from_shape(
        shapely.io.from_geojson(spatial_region_update.geom.model_dump_json())
    )
    other_data = spatial_region_update.model_dump(exclude={"geom"}, exclude_unset=True)
    data = {**other_data, "geom": geom}
    for key, value in data.items():
        setattr(db_spatial_region, key, value)
    session.add(db_spatial_region)
    session.commit()
    session.refresh(db_spatial_region)
    return db_spatial_region


def delete_spatial_region(session: sqlmodel.Session, spatial_region_id: int) -> None:
    """Delete a spatial region."""
    db_item = get_spatial_region(session, spatial_region_id)
    if db_item is not None:
        session.delete(db_item)
        session.commit()
    else:
        raise RuntimeError("Spatial region not found")
