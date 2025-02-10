import datetime as dt
import re

import httpx
import geojson_pydantic
import pyproj
import pytest

from arpav_ppcv.observations_harvester import operations
from arpav_ppcv.schemas import observations


def test_fetch_remote_stations(
    httpx_mock,
    arpav_db_session,
    sample_real_variables,
):
    httpx_mock.add_response(
        url=re.compile(r"https://api.arpa.veneto.it/REST/v1/.*"),
        json={
            "data": [
                {
                    "EPSG4258_LAT": 46.59389393,
                    "EPSG4258_LON": 12.51561664,
                    "altitude": 1342.0,
                    "gaussx": 1769316.0,
                    "gaussy": 5166067.0,
                    "iniziovalidita": "1992-12-11",
                    "statcd": 247,
                    "statnm": "Casamazzagno",
                }
            ],
        },
        status_code=200,
    )
    with httpx.Client() as client:
        fetched = list(
            operations.fetch_remote_stations(
                client,
                sample_real_variables[0:1],
                fetch_stations_with_months=True,
                fetch_stations_with_seasons=False,
                fetch_stations_with_yearly_measurements=False,
            )
        )
        assert list(fetched)[0]["statcd"] == 247


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
            observations.StationCreate(
                code="247",
                geom=geojson_pydantic.Point(
                    type="Point", coordinates=(12.51561664, 46.59389393)
                ),
                altitude_m=1342.0,
                name="Casamazzagno",
                active_since=dt.date(1992, 12, 11),
            ),
        )
    ],
)
def test_parse_station(raw_station, parsed):
    result = operations.parse_station(
        raw_station,
        coord_converter=pyproj.Transformer.from_crs(
            pyproj.CRS("epsg:4258"), pyproj.CRS("epsg:4326"), always_xy=True
        ).transform,
    )
    assert result == parsed
