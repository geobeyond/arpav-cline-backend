import datetime as dt
import logging
from collections.abc import Generator
from typing import (
    Callable,
)

import geojson_pydantic
import httpx
import shapely
import shapely.ops

from ..schemas import (
    observations,
)
from ..schemas.static import (
    MeasurementAggregationType,
    ObservationStationManager,
)

logger = logging.getLogger(__name__)


def fetch_remote_arpafvg_stations(
    client: httpx.Client,
    series_configuration: observations.ObservationSeriesConfiguration,
    arpafvg_observations_base_url: str,
    auth_token: str,
) -> Generator[dict, None, None]:
    # periodo:
    # - 0 means yearly data
    # - 1, 2, 3, 4 means winter, spring, summer, autumn
    indicator_internal_name = [
        obs_name.indicator_observation_name
        for obs_name in series_configuration.climatic_indicator.observation_names
        if obs_name.station_manager == ObservationStationManager.ARPAV
    ][0]
    if (
        series_configuration.measurement_aggregation_type
        == MeasurementAggregationType.YEARLY
    ):
        period = 0
    elif (
        series_configuration.measurement_aggregation_type
        == MeasurementAggregationType.SEASONAL
    ):
        period = 1  # any season works
    else:
        raise NotImplementedError()
    response = client.get(
        f"{arpafvg_observations_base_url}/clima/indicatori/localita",
        headers={
            "authorization": f"Bearer {auth_token}",
        },
        params={
            "indicatore": indicator_internal_name,
            "periodo": period,
        },
    )
    response.raise_for_status()
    for raw_station in response.json().get("data", []):
        yield raw_station


def fetch_remote_arpav_stations(
    client: httpx.Client,
    series_configuration: observations.ObservationSeriesConfiguration,
    arpav_observations_base_url: str,
) -> Generator[dict, None, None]:
    station_url = f"{arpav_observations_base_url}/clima_indicatori/staz_attive_lunghe"
    indicator_internal_name = [
        obs_name.indicator_observation_name
        for obs_name in series_configuration.climatic_indicator.observation_names
        if obs_name.station_manager == ObservationStationManager.ARPAV
    ][0]
    if (
        series_configuration.measurement_aggregation_type
        == MeasurementAggregationType.MONTHLY
    ):
        for month in range(1, 13):
            logger.info(f"Processing month {month}...")
            month_response = client.get(
                station_url,
                params={
                    "indicatore": indicator_internal_name,
                    "tabella": "M",
                    "periodo": str(month),
                },
            )
            month_response.raise_for_status()
            for raw_station in month_response.json().get("data", []):
                yield raw_station
    elif (
        series_configuration.measurement_aggregation_type
        == MeasurementAggregationType.SEASONAL
    ):
        for season in range(1, 5):
            logger.info(f"Processing season {season}...")
            season_response = client.get(
                station_url,
                params={
                    "indicatore": indicator_internal_name,
                    "tabella": "S",
                    "periodo": str(season),
                },
            )
            season_response.raise_for_status()
            for raw_station in season_response.json().get("data", []):
                yield raw_station
    elif (
        series_configuration.measurement_aggregation_type
        == MeasurementAggregationType.YEARLY
    ):
        logger.info("Processing years...")
        year_response = client.get(
            station_url,
            params={
                "indicatore": indicator_internal_name,
                "tabella": "A",
                "periodo": "0",
            },
        )
        year_response.raise_for_status()
        for raw_station in year_response.json().get("data", []):
            yield raw_station
    else:
        raise NotImplementedError(
            f"{series_configuration.measurement_aggregation_type} not implemented"
        )


def parse_arpafvg_station(
    raw_station: dict, coord_converter: Callable
) -> observations.ObservationStationCreate:
    pt_4326 = shapely.Point(raw_station["longitude"], raw_station["latitude"])
    return observations.ObservationStationCreate(
        code=str(raw_station["statid"]),
        geom=geojson_pydantic.Point(type="Point", coordinates=(pt_4326.x, pt_4326.y)),
        managed_by=ObservationStationManager.ARPAFVG,
        altitude_m=raw_station["altitude"],
        name=raw_station["statnm"],
    )


def parse_arpav_station(
    raw_station: dict, coord_converter: Callable
) -> observations.ObservationStationCreate:
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
    return observations.ObservationStationCreate(
        code=station_code,
        geom=geojson_pydantic.Point(type="Point", coordinates=(pt_4326.x, pt_4326.y)),
        managed_by=ObservationStationManager.ARPAV,
        altitude_m=raw_station["altitude"],
        name=raw_station["statnm"],
        active_since=active_since,
        active_until=active_until,
    )


# def harvest_stations(
#     client: httpx.Client,
#     climatic_indicators_to_refresh: Sequence[ClimaticIndicator],
#     fetch_stations_with_months: bool,
#     fetch_stations_with_seasons: bool,
#     fetch_stations_with_yearly_measurements: bool,
# ) -> set[observations.StationCreate]:
#     coord_converter = pyproj.Transformer.from_crs(
#         pyproj.CRS("epsg:4258"), pyproj.CRS("epsg:4326"), always_xy=True
#     ).transform
#     stations = set()
#     for raw_station in fetch_remote_stations(
#         client,
#         climatic_indicators_to_refresh,
#         fetch_stations_with_months,
#         fetch_stations_with_seasons,
#         fetch_stations_with_yearly_measurements,
#     ):
#         stations.add(parse_station(raw_station, coord_converter))
#     return stations
