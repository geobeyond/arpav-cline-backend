import datetime as dt
import logging
from typing import (
    Callable,
    Generator,
    TYPE_CHECKING,
)

import geojson_pydantic
import httpx
import shapely
import shapely.ops

from ..schemas.observations import (
    ObservationMeasurementCreate,
    ObservationSeriesConfiguration,
    ObservationStation,
    ObservationStationCreate,
)
from ..schemas.static import (
    MeasurementAggregationType,
    ObservationStationManager,
    ObservationYearPeriod,
)
from . import common

if TYPE_CHECKING:
    from ..schemas.climaticindicators import ClimaticIndicator

logger = logging.getLogger(__name__)

_STATION_CODE_PROPERTY = "statcd"


def fetch_remote_stations(
    client: httpx.Client,
    series_configuration: ObservationSeriesConfiguration,
    observations_base_url: str,
    ignore_station_codes: list[str] | None = None,
) -> Generator[dict, None, None]:
    station_url = f"{observations_base_url}/clima_indicatori/staz_attive_lunghe"
    indicator_internal_name = common.get_indicator_internal_name(
        series_configuration.climatic_indicator, ObservationStationManager.ARPAV
    )
    station_blacklist = ignore_station_codes or []
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
                raw_code = str(raw_station.get(_STATION_CODE_PROPERTY))
                if raw_code in station_blacklist:
                    logger.info(f"station {raw_code!r} is blacklisted - ignoring...")
                else:
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
                raw_code = str(raw_station.get(_STATION_CODE_PROPERTY))
                if raw_code in station_blacklist:
                    logger.info(f"station {raw_code!r} is blacklisted - ignoring...")
                else:
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
            raw_code = str(raw_station.get(_STATION_CODE_PROPERTY))
            if raw_code in station_blacklist:
                logger.info(f"station {raw_code!r} is blacklisted - ignoring...")
            else:
                yield raw_station
    else:
        raise NotImplementedError(
            f"{series_configuration.measurement_aggregation_type} not implemented"
        )


def parse_station(
    raw_station: dict, coord_converter: Callable
) -> ObservationStationCreate:
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
    return ObservationStationCreate(
        code="-".join(
            (
                ObservationStationManager.ARPAV.value,
                str(raw_station[_STATION_CODE_PROPERTY]),
            )
        ),
        geom=geojson_pydantic.Point(type="Point", coordinates=(pt_4326.x, pt_4326.y)),
        managed_by=ObservationStationManager.ARPAV,
        altitude_m=raw_station["altitude"],
        name=raw_station["statnm"],
        active_since=active_since,
        active_until=active_until,
    )


def fetch_station_measurements(
    client: httpx.Client,
    observation_station: ObservationStation,
    series_configuration: ObservationSeriesConfiguration,
    observations_base_url: str,
) -> Generator[
    tuple[MeasurementAggregationType, ObservationYearPeriod, dict], None, None
]:
    measurements_url = f"{observations_base_url}/clima_indicatori"
    station_identifier = observation_station.code.split("-")[-1]
    indicator_internal_name = common.get_indicator_internal_name(
        series_configuration.climatic_indicator, observation_station.managed_by
    )
    base_params = {
        "statcd": station_identifier,
        "indicatore": indicator_internal_name,
    }
    if (
        aggregation_type := series_configuration.measurement_aggregation_type
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
            yield aggregation_type, ObservationYearPeriod.ALL_YEAR, raw_measurement
    elif aggregation_type == MeasurementAggregationType.SEASONAL:
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
                yield aggregation_type, year_period, raw_measurement
    elif aggregation_type == MeasurementAggregationType.MONTHLY:
        for idx, year_period in enumerate(
            (
                ObservationYearPeriod.JANUARY,
                ObservationYearPeriod.FEBRUARY,
                ObservationYearPeriod.MARCH,
                ObservationYearPeriod.APRIL,
                ObservationYearPeriod.MAY,
                ObservationYearPeriod.JUNE,
                ObservationYearPeriod.JULY,
                ObservationYearPeriod.AUGUST,
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
                yield aggregation_type, year_period, raw_measurement
    else:
        raise NotImplementedError(
            f"measurement aggregation type {aggregation_type!r} not implemented"
        )


def parse_measurement(
    raw_measurement: dict,
    aggregation_type: MeasurementAggregationType,
    year_period: ObservationYearPeriod,
    observation_station: ObservationStation,
    climatic_indicator: "ClimaticIndicator",
) -> ObservationMeasurementCreate:
    """Parse a raw ARPAV measurement.

    Dates are set to the beginning of the corresponding yearly aggregation period.
    """
    parsed_date = common.parse_measurement_date(
        raw_measurement["anno"], aggregation_type, year_period
    )
    return ObservationMeasurementCreate(
        value=raw_measurement["valore"],
        date=parsed_date,
        measurement_aggregation_type=aggregation_type,
        observation_station_id=observation_station.id,
        climatic_indicator_id=climatic_indicator.id,
    )
