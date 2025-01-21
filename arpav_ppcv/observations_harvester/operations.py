import datetime as dt
import logging
from collections.abc import Generator
from typing import Callable

import geojson_pydantic
import httpx
import shapely
import shapely.ops

from .. import (
    exceptions,
)
from ..schemas import (
    climaticindicators,
    observations,
)
from ..schemas.static import (
    MeasurementAggregationType,
    ObservationStationManager,
    ObservationYearPeriod,
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
    indicator_internal_name = _get_indicator_internal_name(
        series_configuration.climatic_indicator, ObservationStationManager.ARPAFVG
    )
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
    if response.status_code != httpx.codes.OK:
        raise exceptions.ObservationDataRetrievalError(
            f"Could not retrieve observation data: {response.status_code - response.text}"
        )
    for raw_station in response.json().get("data", []):
        yield raw_station


def _get_indicator_internal_name(
    climatic_indicator: climaticindicators.ClimaticIndicator,
    station_manager: ObservationStationManager,
) -> str:
    try:
        return [
            obs_name.indicator_observation_name
            for obs_name in climatic_indicator.observation_names
            if obs_name.station_manager == station_manager
        ][0]
    except IndexError as err:
        raise exceptions.ObservationInternalNameNotFoundError(
            f"Could not find an internal name for climatic indicator "
            f"{climatic_indicator.identifier!r} and station "
            f"manager {station_manager}"
        ) from err


def fetch_remote_arpav_stations(
    client: httpx.Client,
    series_configuration: observations.ObservationSeriesConfiguration,
    arpav_observations_base_url: str,
) -> Generator[dict, None, None]:
    station_url = f"{arpav_observations_base_url}/clima_indicatori/staz_attive_lunghe"
    indicator_internal_name = _get_indicator_internal_name(
        series_configuration.climatic_indicator, ObservationStationManager.ARPAV
    )
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


def fetch_arpav_station_measurements(
    client: httpx.Client,
    observation_station: observations.ObservationStation,
    series_configuration: observations.ObservationSeriesConfiguration,
    arpav_observations_base_url: str,
) -> Generator[tuple[ObservationYearPeriod, dict], None, None]:
    measurements_url = f"{arpav_observations_base_url}/clima_indicatori"
    station_identifier = observation_station.code.split("-")[-1]
    indicator_internal_name = _get_indicator_internal_name(
        series_configuration.climatic_indicator, observation_station.managed_by
    )
    base_params = {
        "statcd": station_identifier,
        "indicatore": indicator_internal_name,
    }
    if (
        aggreg_type := series_configuration.measurement_aggregation_type
    ) == MeasurementAggregationType.YEARLY:
        response = client.get(
            measurements_url,
            params={
                **base_params,
                "tabella": "A",
                "periodo": "0",
            },
        )
        response.raise_for_status()
        for raw_measurement in response.json().get("data", []):
            yield ObservationYearPeriod.ALL_YEAR, raw_measurement
    elif aggreg_type == MeasurementAggregationType.SEASONAL:
        for idx, year_period in enumerate(
            (
                ObservationYearPeriod.WINTER,
                ObservationYearPeriod.SPRING,
                ObservationYearPeriod.SUMMER,
                ObservationYearPeriod.AUTUMN,
            )
        ):
            response = client.get(
                measurements_url,
                params={
                    **base_params,
                    "tabella": "S",
                    "periodo": idx + 1,
                },
            )
            response.raise_for_status()
            for raw_measurement in response.json().get("data", []):
                yield year_period, raw_measurement
    elif aggreg_type == MeasurementAggregationType.MONTHLY:
        for idx, year_period in enumerate(
            (
                ObservationYearPeriod.JANUARY,
                ObservationYearPeriod.FEBRUARY,
                ObservationYearPeriod.MARCH,
                ObservationYearPeriod.APRIL,
                ObservationYearPeriod.MAY,
                ObservationYearPeriod.JUNE,
                ObservationYearPeriod.JULY,
                ObservationYearPeriod.AUTUMN,
                ObservationYearPeriod.SEPTEMBER,
                ObservationYearPeriod.OCTOBER,
                ObservationYearPeriod.NOVEMBER,
                ObservationYearPeriod.DECEMBER,
            )
        ):
            response = client.get(
                measurements_url,
                params={
                    **base_params,
                    "tabella": "M",
                    "periodo": idx + 1,
                },
            )
            response.raise_for_status()
            for raw_measurement in response.json().get("data", []):
                yield year_period, raw_measurement
    else:
        raise NotImplementedError(
            f"measurement aggregation type {aggreg_type!r} not implemented"
        )


def fetch_arpafvg_station_measurements(
    client: httpx.Client,
    observation_station: observations.ObservationStation,
    series_configuration: observations.ObservationSeriesConfiguration,
    arpafvg_observations_base_url: str,
    auth_token: str,
) -> Generator[tuple[ObservationYearPeriod, dict], None, None]:
    measurements_url = f"{arpafvg_observations_base_url}/clima/indicatori/dati"
    headers = {"Authorization": f"Bearer {auth_token}"}
    station_identifier = observation_station.code.split("-")[-1]
    indicator_internal_name = _get_indicator_internal_name(
        series_configuration.climatic_indicator, observation_station.managed_by
    )
    base_params = {
        "statid": station_identifier,
        "indicatore": indicator_internal_name,
    }
    if (
        aggreg_type := series_configuration.measurement_aggregation_type
    ) == MeasurementAggregationType.YEARLY:
        response = client.get(
            measurements_url,
            headers=headers,
            params={
                **base_params,
                "tabella": "A",
                "periodo": "0",
            },
        )
        response.raise_for_status()
        for raw_measurement in response.json():
            yield ObservationYearPeriod.ALL_YEAR, raw_measurement
    elif aggreg_type == MeasurementAggregationType.SEASONAL:
        for idx, year_period in enumerate(
            (
                ObservationYearPeriod.WINTER,
                ObservationYearPeriod.SPRING,
                ObservationYearPeriod.SUMMER,
                ObservationYearPeriod.AUTUMN,
            )
        ):
            response = client.get(
                measurements_url,
                headers=headers,
                params={
                    **base_params,
                    "tabella": "S",
                    "periodo": idx + 1,
                },
            )
            response.raise_for_status()
            for raw_measurement in response.json():
                yield year_period, raw_measurement
    elif aggreg_type == MeasurementAggregationType.MONTHLY:
        yield None  # ARPA_FVG observation stations do not have monthly data
    else:
        raise NotImplementedError(
            f"measurement aggregation type {aggreg_type!r} not implemented"
        )


def _parse_measurement_date(
    raw_year: int,
    year_period: ObservationYearPeriod,
) -> tuple[dt.date, MeasurementAggregationType]:
    """Parse a raw measurement date.

    Dates are set to the beginning of the corresponding yearly aggregation
    period.
    """
    return {
        ObservationYearPeriod.ALL_YEAR: (
            dt.date(raw_year, 1, 1),
            MeasurementAggregationType.YEARLY,
        ),
        ObservationYearPeriod.WINTER: (
            dt.date(raw_year, 12, 1),
            MeasurementAggregationType.SEASONAL,
        ),
        ObservationYearPeriod.SPRING: (
            dt.date(raw_year, 3, 1),
            MeasurementAggregationType.SEASONAL,
        ),
        ObservationYearPeriod.SUMMER: (
            dt.date(raw_year, 6, 1),
            MeasurementAggregationType.SEASONAL,
        ),
        ObservationYearPeriod.AUTUMN: (
            dt.date(raw_year, 9, 1),
            MeasurementAggregationType.SEASONAL,
        ),
        ObservationYearPeriod.JANUARY: (
            dt.date(raw_year, 1, 1),
            MeasurementAggregationType.MONTHLY,
        ),
        ObservationYearPeriod.FEBRUARY: (
            dt.date(raw_year, 2, 1),
            MeasurementAggregationType.MONTHLY,
        ),
        ObservationYearPeriod.MARCH: (
            dt.date(raw_year, 3, 1),
            MeasurementAggregationType.MONTHLY,
        ),
        ObservationYearPeriod.APRIL: (
            dt.date(raw_year, 4, 1),
            MeasurementAggregationType.MONTHLY,
        ),
        ObservationYearPeriod.MAY: (
            dt.date(raw_year, 5, 1),
            MeasurementAggregationType.MONTHLY,
        ),
        ObservationYearPeriod.JUNE: (
            dt.date(raw_year, 6, 1),
            MeasurementAggregationType.MONTHLY,
        ),
        ObservationYearPeriod.JULY: (
            dt.date(raw_year, 7, 1),
            MeasurementAggregationType.MONTHLY,
        ),
        ObservationYearPeriod.AUGUST: (
            dt.date(raw_year, 8, 1),
            MeasurementAggregationType.MONTHLY,
        ),
        ObservationYearPeriod.SEPTEMBER: (
            dt.date(raw_year, 9, 1),
            MeasurementAggregationType.MONTHLY,
        ),
        ObservationYearPeriod.OCTOBER: (
            dt.date(raw_year, 10, 1),
            MeasurementAggregationType.MONTHLY,
        ),
        ObservationYearPeriod.NOVEMBER: (
            dt.date(raw_year, 11, 1),
            MeasurementAggregationType.MONTHLY,
        ),
        ObservationYearPeriod.DECEMBER: (
            dt.date(raw_year, 12, 1),
            MeasurementAggregationType.MONTHLY,
        ),
    }.get(year_period)


def parse_arpafvg_measurement(
    raw_measurement: dict,
    year_period: ObservationYearPeriod,
    observation_station: observations.ObservationStation,
    climatic_indicator: climaticindicators.ClimaticIndicator,
) -> observations.ObservationMeasurementCreate:
    parsed_date, aggreg_type = _parse_measurement_date(
        raw_measurement["anno"], year_period
    )
    return observations.ObservationMeasurementCreate(
        value=raw_measurement["valore"],
        date=parsed_date,
        measurement_aggregation_type=aggreg_type,
        observation_station_id=observation_station.id,
        climatic_indicator_id=climatic_indicator.id,
    )


def parse_arpav_measurement(
    raw_measurement: dict,
    year_period: ObservationYearPeriod,
    observation_station: observations.ObservationStation,
    climatic_indicator: climaticindicators.ClimaticIndicator,
) -> observations.ObservationMeasurementCreate:
    """Parse a raw ARPAV measurement.

    Dates are set to the beginning of the corresponding yearly aggregation period.
    """
    parsed_date, aggreg_type = _parse_measurement_date(
        raw_measurement["anno"], year_period
    )
    return observations.ObservationMeasurementCreate(
        value=raw_measurement["valore"],
        date=parsed_date,
        measurement_aggregation_type=aggreg_type,
        observation_station_id=observation_station.id,
        climatic_indicator_id=climatic_indicator.id,
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
