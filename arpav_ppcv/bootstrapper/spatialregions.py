import json
from pathlib import Path

import geojson_pydantic
import shapely.geometry
import shapely.io
import shapely.ops

from ..schemas.base import SpatialRegionCreate


def generate_spatial_regions(geoms_base_path: Path) -> list[SpatialRegionCreate]:
    return [
        SpatialRegionCreate(
            name="arpa_fvg",
            internal_value="FVG",
            display_name_english="ARPA Friuli Venezia Giulia",
            display_name_italian="ARPA Friuli Venezia Giulia",
            sort_order=0,
            geom=_geom_to_pydantic(
                _load_geojson_bounds(geoms_base_path / "arpafvg.geojson")
            ),
        ),
        SpatialRegionCreate(
            name="arpa_taa",
            internal_value="TAA",
            display_name_english="ARPA Trentino-Alto Adige",
            display_name_italian="ARPA Trentino-Alto Adige",
            sort_order=1,
            geom=_geom_to_pydantic(
                _load_geojson_bounds(geoms_base_path / "arpataa.geojson")
            ),
        ),
        SpatialRegionCreate(
            name="arpa_v",
            internal_value="V",
            display_name_english="ARPA Veneto",
            display_name_italian="ARPA Veneto",
            sort_order=2,
            geom=_geom_to_pydantic(
                _load_geojson_bounds(geoms_base_path / "arpav.geojson")
            ),
        ),
        SpatialRegionCreate(
            name="arpa_vfvg",
            internal_value="VFVG",
            display_name_english="Combined ARPA Veneto and ARPA Friuli Venezia Giulia",
            display_name_italian="Combinato ARPA Veneto e ARPA Friuli Venezia Giulia",
            sort_order=2,
            geom=_geom_to_pydantic(
                _combine_geoms(
                    _load_geojson_bounds(geoms_base_path / "arpav.geojson"),
                    _load_geojson_bounds(geoms_base_path / "arpafvg.geojson"),
                )
            ),
        ),
        SpatialRegionCreate(
            name="arpa_vfvgtaa",
            internal_value="VFVGTAA",
            display_name_english=(
                "Combined ARPA Veneto, ARPA Friuli Venezia Giulia and ARPA "
                "Trentino-Alto Adige"
            ),
            display_name_italian=(
                "Combinato ARPA Veneto, ARPA Friuli Venezia Giulia e "
                "ARPA Trentino-Alto Adige"
            ),
            sort_order=2,
            geom=_geom_to_pydantic(
                _combine_geoms(
                    _load_geojson_bounds(geoms_base_path / "arpav.geojson"),
                    _load_geojson_bounds(geoms_base_path / "arpafvg.geojson"),
                    _load_geojson_bounds(geoms_base_path / "arpataa.geojson"),
                )
            ),
        ),
    ]


def _load_geojson_bounds(geojson_file: Path) -> shapely.geometry.MultiPolygon:
    return shapely.io.from_geojson(geojson_file.read_bytes())


def _geom_to_pydantic(
    geom: shapely.geometry.MultiPolygon,
) -> geojson_pydantic.MultiPolygon:
    return geojson_pydantic.MultiPolygon(
        type="MultiPolygon",
        coordinates=json.loads(shapely.io.to_geojson(geom))["coordinates"],
    )


def _combine_geoms(
    *geoms: shapely.geometry.MultiPolygon,
) -> shapely.geometry.MultiPolygon:
    return shapely.ops.unary_union(geoms)
