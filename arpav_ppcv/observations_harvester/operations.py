import datetime as dt
import logging
from collections.abc import (
    Generator,
    Sequence,
)
from typing import (
    Callable,
)

import geojson_pydantic
import httpx
import pyproj
import shapely
import shapely.ops

from ..schemas import observations

logger = logging.getLogger(__name__)


def fetch_remote_stations(
    client: httpx.Client,
    variables: Sequence[observations.Variable],
    fetch_stations_with_months: bool,
    fetch_stations_with_seasons: bool,
    fetch_stations_with_yearly_measurements: bool,
) -> Generator[dict, None, None]:
    station_url = (
        "https://api.arpa.veneto.it/REST/v1/clima_indicatori/staz_attive_lunghe"
    )
    for variable in variables:
        logger.info(
            f"Retrieving stations with monthly measurements for variable "
            f"{variable.name!r}..."
        )
        if fetch_stations_with_months:
            for month in range(1, 13):
                logger.info(f"Processing month {month}...")
                month_response = client.get(
                    station_url,
                    params={
                        "indicatore": variable.name,
                        "tabella": "M",
                        "periodo": str(month),
                    },
                )
                month_response.raise_for_status()
                for raw_station in month_response.json().get("data", []):
                    yield raw_station
        if fetch_stations_with_seasons:
            for season in range(1, 5):
                logger.info(f"Processing season {season}...")
                season_response = client.get(
                    station_url,
                    params={
                        "indicatore": variable.name,
                        "tabella": "S",
                        "periodo": str(season),
                    },
                )
                season_response.raise_for_status()
                for raw_station in season_response.json().get("data", []):
                    yield raw_station
        if fetch_stations_with_yearly_measurements:
            logger.info("Processing year...")
            year_response = client.get(
                station_url,
                params={
                    "indicatore": variable.name,
                    "tabella": "A",
                    "periodo": "0",
                },
            )
            year_response.raise_for_status()
            for raw_station in year_response.json().get("data", []):
                yield raw_station


def parse_station(
    raw_station: dict, coord_converter: Callable
) -> observations.StationCreate:
    station_code = str(raw_station["statcd"])
    if raw_start := raw_station.get("iniziovalidita"):
        try:
            active_since = dt.date(*(int(i) for i in raw_start.split("-")))
        except TypeError:
            logger.warning(
                f"Could not extract a valid date from the input {raw_start!r}"
            )
            active_since = None
    else:
        active_since = None
    if raw_end := raw_station.get("finevalidita"):
        try:
            active_until = dt.date(*raw_end.split("-"))
        except TypeError:
            logger.warning(f"Could not extract a valid date from the input {raw_end!r}")
            active_until = None
    else:
        active_until = None
    pt_4258 = shapely.Point(raw_station["EPSG4258_LON"], raw_station["EPSG4258_LAT"])
    pt_4326 = shapely.ops.transform(coord_converter, pt_4258)
    return observations.StationCreate(
        code=station_code,
        geom=geojson_pydantic.Point(type="Point", coordinates=(pt_4326.x, pt_4326.y)),
        altitude_m=raw_station["altitude"],
        name=raw_station["statnm"],
        type_=raw_station.get("stattype", "").lower().replace(" ", "_"),
        active_since=active_since,
        active_until=active_until,
    )


def harvest_stations(
    client: httpx.Client,
    variables_to_refresh: Sequence[observations.Variable],
    fetch_stations_with_months: bool,
    fetch_stations_with_seasons: bool,
    fetch_stations_with_yearly_measurements: bool,
) -> set[observations.StationCreate]:
    coord_converter = pyproj.Transformer.from_crs(
        pyproj.CRS("epsg:4258"), pyproj.CRS("epsg:4326"), always_xy=True
    ).transform
    stations = set()
    for raw_station in fetch_remote_stations(
        client,
        variables_to_refresh,
        fetch_stations_with_months,
        fetch_stations_with_seasons,
        fetch_stations_with_yearly_measurements,
    ):
        stations.add(parse_station(raw_station, coord_converter))
    return stations
