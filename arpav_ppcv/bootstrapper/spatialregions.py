import json
from pathlib import Path

import geojson_pydantic

from ..schemas.base import SpatialRegionCreate


def _load_geojson_bounds(geojson_file: Path) -> geojson_pydantic.MultiPolygon:
    with geojson_file.open(mode="r") as fh:
        bounds = json.load(fh)
        return geojson_pydantic.MultiPolygon(
            type="MultiPolygon", coordinates=bounds["geometry"]["coordinates"]
        )


def generate_spatial_regions(geoms_base_path: Path) -> list[SpatialRegionCreate]:
    return [
        SpatialRegionCreate(
            name="arpafvg",
            display_name_english="ARPA Friuli Venezia Giulia",
            display_name_italian="ARPA Friuli Venezia Giulia",
            sort_order=0,
            geom=_load_geojson_bounds(geoms_base_path / "arpafvg.geojson"),
        ),
        SpatialRegionCreate(
            name="arpataa",
            display_name_english="ARPA Trentino-Alto Adige",
            display_name_italian="ARPA Trentino-Alto Adige",
            sort_order=1,
            geom=_load_geojson_bounds(geoms_base_path / "arpataa.geojson"),
        ),
        SpatialRegionCreate(
            name="arpav",
            display_name_english="ARPA Veneto",
            display_name_italian="ARPA Veneto",
            sort_order=2,
            geom=_load_geojson_bounds(geoms_base_path / "arpav.geojson"),
        ),
    ]
