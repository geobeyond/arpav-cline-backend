import logging
from typing import (
    Generator,
    Optional,
    TYPE_CHECKING,
)

import geojson_pydantic
import httpx
import shapely

from .. import exceptions
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


def fetch_remote_stations(
    client: httpx.Client,
    series_configuration: ObservationSeriesConfiguration,
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
    elif (
        series_configuration.measurement_aggregation_type
        == MeasurementAggregationType.MONTHLY
    ):
        period = 1  # any month works
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
    raw_station: dict,
) -> ObservationStationCreate:
    pt_4326 = shapely.Point(raw_station["longitude"], raw_station["latitude"])
    return ObservationStationCreate(
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
    observation_station: ObservationStation,
    series_configuration: ObservationSeriesConfiguration,
    observations_base_url: str,
    auth_token: str,
) -> Generator[tuple[Optional[ObservationYearPeriod], Optional[dict]], None, None]:
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
        yield (None, None)  # ARPA_FVG observation stations do not have monthly data
    else:
        raise NotImplementedError(
            f"measurement aggregation type {aggreg_type!r} not implemented"
        )


def parse_measurement(
    raw_measurement: dict,
    aggregation_type: MeasurementAggregationType,
    year_period: ObservationYearPeriod,
    observation_station: ObservationStation,
    climatic_indicator: "ClimaticIndicator",
) -> ObservationMeasurementCreate:
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
