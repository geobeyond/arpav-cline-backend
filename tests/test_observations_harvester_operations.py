import datetime as dt

import geojson_pydantic
import pyproj
import pytest

from arpav_cline.observations_harvester import arpav as arpav_operations
from arpav_cline.schemas import (
    observations,
    static,
)


@pytest.mark.parametrize(
    "raw_station, parsed",
    [
        pytest.param(
            {
                "EPSG4258_LAT": 46.59389393,
                "EPSG4258_LON": 12.51561664,
                "altitude": 1342.0,
                "gaussx": 1769316.0,
                "gaussy": 5166067.0,
                "iniziovalidita": "1992-12-11",
                "statcd": 247,
                "statnm": "Casamazzagno",
            },
            observations.ObservationStationCreate(
                code="arpa_v-247",
                geom=geojson_pydantic.Point(
                    type="Point", coordinates=(12.51561664, 46.59389393)
                ),
                altitude_m=1342.0,
                name="Casamazzagno",
                active_since=dt.date(1992, 12, 11),
                managed_by=static.ObservationStationManager.ARPAV,
            ),
        )
    ],
)
def test_parse_station(raw_station, parsed):
    result = arpav_operations.parse_station(
        raw_station,
        coord_converter=pyproj.Transformer.from_crs(
            pyproj.CRS("epsg:4258"), pyproj.CRS("epsg:4326"), always_xy=True
        ).transform,
    )
    assert result == parsed
