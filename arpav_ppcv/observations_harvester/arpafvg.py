import logging
from typing import (
    Callable,
    Generator,
)

import geojson_pydantic
import httpx
import shapely

from .. import exceptions
from ..schemas import (
    climaticindicators,
    observations,
)
from ..schemas.static import (
    MeasurementAggregationType,
    ObservationStationManager,
    ObservationYearPeriod,
)
from . import common

logger = logging.getLogger(__name__)


def fetch_remote_stations(
    client: httpx.Client,
    series_configuration: observations.ObservationSeriesConfiguration,
    observations_base_url: str,
    auth_token: str,
) -> Generator[dict, None, None]:
    # periodo:
    # - 0 means yearly data
    # - 1, 2, 3, 4 means winter, spring, summer, autumn
    indicator_internal_name = common.get_indicator_internal_name(
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
        f"{observations_base_url}/clima/indicatori/localita",
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


def parse_station(
    raw_station: dict, coord_converter: Callable
) -> observations.ObservationStationCreate:
    pt_4326 = shapely.Point(raw_station["longitude"], raw_station["latitude"])
    return observations.ObservationStationCreate(
        code="-".join(
            (
                ObservationStationManager.ARPAFVG.value,
                str(raw_station["statid"]),
            )
        ),
        geom=geojson_pydantic.Point(type="Point", coordinates=(pt_4326.x, pt_4326.y)),
        managed_by=ObservationStationManager.ARPAFVG,
        altitude_m=raw_station["altitude"],
        name=raw_station["statnm"],
    )


def fetch_station_measurements(
    client: httpx.Client,
    observation_station: observations.ObservationStation,
    series_configuration: observations.ObservationSeriesConfiguration,
    observations_base_url: str,
    auth_token: str,
) -> Generator[tuple[ObservationYearPeriod, dict], None, None]:
    measurements_url = f"{observations_base_url}/clima/indicatori/dati"
    headers = {"Authorization": f"Bearer {auth_token}"}
    station_identifier = observation_station.code.split("-")[-1]
    indicator_internal_name = common.get_indicator_internal_name(
        series_configuration.climatic_indicator, observation_station.managed_by
    )
    base_params = {
        "statid": station_identifier,
        "indicatore": indicator_internal_name,
    }
    logger.warning(f"{measurements_url=}")
    logger.warning(f"{headers=}")
    logger.warning(f"{station_identifier=}")
    logger.warning(f"{indicator_internal_name=}")
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
            logger.warning(f"{raw_measurement=}")
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


def parse_measurement(
    raw_measurement: dict,
    year_period: ObservationYearPeriod,
    observation_station: observations.ObservationStation,
    climatic_indicator: climaticindicators.ClimaticIndicator,
) -> observations.ObservationMeasurementCreate:
    parsed_date, aggreg_type = common.parse_measurement_date(
        raw_measurement["anno"], year_period
    )
    return observations.ObservationMeasurementCreate(
        value=raw_measurement["valore"],
        date=parsed_date,
        measurement_aggregation_type=aggreg_type,
        observation_station_id=observation_station.id,
        climatic_indicator_id=climatic_indicator.id,
    )
