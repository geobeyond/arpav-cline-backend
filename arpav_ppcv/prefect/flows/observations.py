import datetime as dt
from typing import (
    Sequence,
    Union,
)

import httpx
import sqlmodel
import prefect
import prefect.artifacts
import pyproj

from arpav_ppcv import database
from arpav_ppcv.config import get_settings
from arpav_ppcv.observations_harvester import operations
from arpav_ppcv.operations import (
    create_db_schema,
    refresh_station_climatic_indicator_database_view,
)
from arpav_ppcv.schemas import (
    base,
    climaticindicators,
    observations,
)
from arpav_ppcv.schemas.static import ObservationStationManager

# this is a module global because we need to configure the prefect flow and
# task with values from it
settings = get_settings()
db_engine = database.get_engine(settings)


@prefect.task(
    retries=settings.prefect.num_task_retries,
    retry_delay_seconds=settings.prefect.task_retry_delay_seconds,
)
def harvest_stations(
    client: httpx.Client,
    series_configuration: observations.ObservationSeriesConfiguration,
) -> set[observations.ObservationStationCreate]:
    coord_converter = pyproj.Transformer.from_crs(
        pyproj.CRS("epsg:4258"), pyproj.CRS("epsg:4326"), always_xy=True
    ).transform
    stations = set()
    for station_manager in series_configuration.station_managers:
        if station_manager == ObservationStationManager.ARPAV:
            retriever = operations.fetch_remote_arpav_stations(
                client,
                series_configuration,
                arpav_observations_base_url=settings.arpav_observations_base_url,
            )
            for raw_station in retriever:
                stations.add(
                    operations.parse_arpav_station(raw_station, coord_converter)
                )
        elif station_manager == ObservationStationManager.ARPAFVG:
            retriever = operations.fetch_remote_arpafvg_stations(
                client,
                series_configuration,
                arpafvg_observations_base_url=settings.arpafvg_observations_base_url,
                auth_token=settings.arpafvg_auth_token,
            )
            for raw_station in retriever:
                stations.add(
                    operations.parse_arpafvg_station(raw_station, coord_converter)
                )
        else:
            raise NotImplementedError(
                f"Observation stations managed by {station_manager} are not "
                f"implemented."
            )
    return stations


@prefect.task(
    retries=settings.prefect.num_task_retries,
    retry_delay_seconds=settings.prefect.task_retry_delay_seconds,
)
def find_new_stations(
    db_stations: Sequence[observations.ObservationStation],
    new_stations: Sequence[observations.ObservationStationCreate],
) -> list[observations.ObservationStationCreate]:
    possibly_new_stations = {(s.managed_by, s.code): s for s in new_stations}
    existing_stations = {(s.managed_by, s.code): s for s in db_stations}
    to_create = []
    for possibly_new_station in possibly_new_stations.values():
        if (
            existing_stations.get(
                (possibly_new_station.managed_by, possibly_new_station.code)
            )
            is None
        ):
            print(
                f"About to create station {possibly_new_station.managed_by} "
                f"{possibly_new_station.code} - {possibly_new_station.name}..."
            )
            to_create.append(possibly_new_station)
        else:
            print(
                f"Station {possibly_new_station.managed_by} "
                f"{possibly_new_station.code} - {possibly_new_station.name} "
                f"is already known"
            )
    for existing_station in existing_stations.values():
        if (
            possibly_new_stations.get((existing_station.managed_by, existing_station.code))
            is None
        ):
            print(
                f"Station {existing_station.identifier} is not "
                f"found on the remote. Maybe it can be deleted? The system does not "
                f"delete stations so please check manually if this should be deleted "
                f"or not"
            )
    return to_create


@prefect.flow(
    log_prints=True,
    retries=settings.prefect.num_flow_retries,
    retry_delay_seconds=settings.prefect.flow_retry_delay_seconds,
)
def refresh_stations(observation_series_configuration_identifier: str | None = None):
    client = httpx.Client()
    with sqlmodel.Session(db_engine) as db_session:
        db_series_configurations = _get_observation_series_configurations(
            db_session, observation_series_configuration_identifier
        )
        if len(db_series_configurations) > 0:
            to_filter_for_new_stations = set()
            to_wait_on = []
            for series_conf in db_series_configurations:
                print(
                    f"refreshing stations that are part of series "
                    f"{series_conf.identifier!r}..."
                )
                fut = harvest_stations.submit(client, series_conf)
                to_wait_on.append(fut)
            for future in to_wait_on:
                to_filter_for_new_stations.update(future.result())
            to_create = find_new_stations(
                database.collect_all_observation_stations(db_session),
                list(to_filter_for_new_stations),
            )
            if len(to_create) > 0:
                print(f"Found {len(to_create)} new stations. Creating them now...")
                for s in to_create:
                    print(f"- ({s.code}) {s.name}")
                created = database.create_many_observation_stations(
                    db_session, to_create
                )
            else:
                created = []
                print("No new stations found.")
            prefect.artifacts.create_table_artifact(
                key="stations-created",
                table=[
                    {"id": str(s.id), "identifier": s.identifier, "name": s.name} for s in created
                ],
                description=f"# Created {len(created)} stations",
            )
        else:
            print("There are no variables to process, skipping...")


@prefect.task(
    retries=settings.prefect.num_task_retries,
    retry_delay_seconds=settings.prefect.task_retry_delay_seconds,
)
def harvest_monthly_measurements(
    client: httpx.Client,
    db_session: sqlmodel.Session,
    station: observations.Station,
    climatic_indicator: climaticindicators.ClimaticIndicator,
    month: int,
) -> list[observations.MonthlyMeasurementCreate]:
    existing_measurements = database.collect_all_monthly_measurements(
        db_session,
        station_id_filter=station.id,
        climatic_indicator_id_filter=climatic_indicator.id,
        month_filter=month,
    )
    existing = {}
    for db_measurement in existing_measurements:
        measurement_id = build_monthly_measurement_id(db_measurement)
        existing[measurement_id] = db_measurement
    response = client.get(
        "https://api.arpa.veneto.it/REST/v1/clima_indicatori",
        params={
            "statcd": station.code,
            "indicatore": climatic_indicator.name,
            "tabella": "M",
            "periodo": month,
        },
    )
    response.raise_for_status()
    to_create = []
    for raw_measurement in response.json().get("data", []):
        measurement_create = observations.MonthlyMeasurementCreate(
            station_id=station.id,
            climatic_indicator_id=climatic_indicator.id,
            value=raw_measurement["valore"],
            date=dt.date(raw_measurement["anno"], month, 1),
        )
        measurement_id = build_monthly_measurement_id(measurement_create)
        if measurement_id not in existing:
            to_create.append(measurement_create)
    return to_create


@prefect.flow(
    log_prints=True,
    retries=settings.prefect.num_flow_retries,
    retry_delay_seconds=settings.prefect.flow_retry_delay_seconds,
)
def refresh_measurements(
    station_code: str | None = None,
    observation_series_configuration_identifier: str | None = None,
):
    pass


@prefect.flow(
    log_prints=True,
    retries=settings.prefect.num_flow_retries,
    retry_delay_seconds=settings.prefect.flow_retry_delay_seconds,
)
def refresh_monthly_measurements(
    station_code: str | None = None,
    climatic_indicator_identifier: str | None = None,
    month: int | None = None,
):
    client = httpx.Client()
    all_created = []
    with sqlmodel.Session(db_engine) as db_session:
        if (
            len(
                db_climatic_indicators := _get_climatic_indicators(
                    db_session, climatic_indicator_identifier
                )
            )
            > 0
        ):
            if len(db_stations := _get_stations(db_session, station_code)) > 0:
                for db_station in db_stations:
                    to_create = []
                    to_wait_for = []
                    print(f"Processing station: {db_station.name!r}...")
                    for db_climatic_indicator in db_climatic_indicators:
                        print(
                            f"Processing climatic indicator: {db_climatic_indicator.identifier!r}..."
                        )
                        if len(months := _get_months(month)) > 0:
                            for current_month in months:
                                print(f"Processing month: {current_month!r}...")
                                fut = harvest_monthly_measurements.submit(
                                    client,
                                    db_session,
                                    db_station,
                                    db_climatic_indicator,
                                    current_month,
                                )
                                to_wait_for.append(fut)
                        else:
                            print("There are no months to process, skipping...")
                    for future in to_wait_for:
                        to_create.extend(future.result())
                    print(f"creating {len(to_create)} new monthly measurements...")
                    created = database.create_many_monthly_measurements(
                        db_session, to_create
                    )
                    all_created.extend(created)
            else:
                print("There are no stations to process, skipping...")
        else:
            print("There are no variables to process, skipping...")
        prefect.artifacts.create_table_artifact(
            key="monthly-measurements-created",
            table=_build_created_measurements_table(all_created),
            description=f"# Created {len(all_created)} monthly measurements",
        )


@prefect.task(
    retries=settings.prefect.num_task_retries,
    retry_delay_seconds=settings.prefect.task_retry_delay_seconds,
)
def harvest_seasonal_measurements(
    client: httpx.Client,
    db_session: sqlmodel.Session,
    station: observations.Station,
    climatic_indicator: climaticindicators.ClimaticIndicator,
    season: base.Season,
) -> list[observations.SeasonalMeasurementCreate]:
    existing_measurements = database.collect_all_seasonal_measurements(
        db_session,
        station_id_filter=station.id,
        climatic_indicator_id_filter=climatic_indicator.id,
        season_filter=season,
    )
    existing = {}
    for db_measurement in existing_measurements:
        measurement_id = build_seasonal_measurement_id(db_measurement)
        existing[measurement_id] = db_measurement

    season_query_param = {
        base.Season.WINTER: 1,
        base.Season.SPRING: 2,
        base.Season.SUMMER: 3,
        base.Season.AUTUMN: 4,
    }[season]
    response = client.get(
        "https://api.arpa.veneto.it/REST/v1/clima_indicatori",
        params={
            "statcd": station.code,
            "indicatore": climatic_indicator.name,
            "tabella": "S",
            "periodo": season_query_param,
        },
    )
    response.raise_for_status()
    to_create = []
    for raw_measurement in response.json().get("data", []):
        measurement_create = observations.SeasonalMeasurementCreate(
            station_id=station.id,
            climatic_indicator_id=climatic_indicator.id,
            value=raw_measurement["valore"],
            year=int(raw_measurement["anno"]),
            season=season,
        )
        measurement_id = build_seasonal_measurement_id(measurement_create)
        if measurement_id not in existing:
            to_create.append(measurement_create)
    return to_create


@prefect.flow(
    log_prints=True,
    retries=settings.prefect.num_flow_retries,
    retry_delay_seconds=settings.prefect.flow_retry_delay_seconds,
)
def refresh_seasonal_measurements(
    station_code: str | None = None,
    climatic_indicator_name: str | None = None,
    season_name: str | None = None,
):
    client = httpx.Client()
    all_created = []
    with sqlmodel.Session(db_engine) as db_session:
        if (
            len(
                db_climatic_indicators := _get_climatic_indicators(
                    db_session, climatic_indicator_name
                )
            )
            > 0
        ):
            if len(db_stations := _get_stations(db_session, station_code)) > 0:
                for db_station in db_stations:
                    to_create = []
                    to_wait_for = []
                    print(f"Processing station: {db_station.name!r}...")
                    for db_climatic_indicator in db_climatic_indicators:
                        print(
                            f"Processing climatic indicator: {db_climatic_indicator.identifier!r}..."
                        )
                        if len(seasons := _get_seasons(season_name)) > 0:
                            for season in seasons:
                                print(f"Processing season: {season!r}...")
                                fut = harvest_seasonal_measurements.submit(
                                    client,
                                    db_session,
                                    db_station,
                                    db_climatic_indicator,
                                    season,
                                )
                                to_wait_for.append(fut)
                        else:
                            print("There are no seasons to process, skipping...")
                    for future in to_wait_for:
                        to_create.extend(future.result())
                    print(f"creating {len(to_create)} new seasonal measurements...")
                    created = database.create_many_seasonal_measurements(
                        db_session, to_create
                    )
                    all_created.extend(created)
            else:
                print("There are no stations to process, skipping...")
        else:
            print("There are no variables to process, skipping...")
        prefect.artifacts.create_table_artifact(
            key="seasonal-measurements-created",
            table=_build_created_measurements_table(all_created),
            description=f"# Created {len(all_created)} seasonal measurements",
        )


@prefect.task(
    retries=settings.prefect.num_task_retries,
    retry_delay_seconds=settings.prefect.task_retry_delay_seconds,
)
def harvest_yearly_measurements(
    client: httpx.Client,
    db_session: sqlmodel.Session,
    station: observations.Station,
    climatic_indicator: climaticindicators.ClimaticIndicator,
) -> list[observations.YearlyMeasurementCreate]:
    to_create = []
    existing_measurements = database.collect_all_yearly_measurements(
        db_session,
        station_id_filter=station.id,
        climatic_indicator_id_filter=climatic_indicator.id,
    )
    existing = {}
    for db_measurement in existing_measurements:
        measurement_id = build_yearly_measurement_id(db_measurement)
        existing[measurement_id] = db_measurement
    response = client.get(
        "https://api.arpa.veneto.it/REST/v1/clima_indicatori",
        params={
            "statcd": station.code,
            "indicatore": climatic_indicator.name,
            "tabella": "A",
            "periodo": "0",
        },
    )
    response.raise_for_status()
    for raw_measurement in response.json().get("data", []):
        yearly_measurement_create = observations.YearlyMeasurementCreate(
            station_id=station.id,
            climatic_indicator_id=climatic_indicator.id,
            value=raw_measurement["valore"],
            year=int(raw_measurement["anno"]),
        )
        measurement_id = build_yearly_measurement_id(yearly_measurement_create)
        if measurement_id not in existing:
            to_create.append(yearly_measurement_create)
    return to_create


@prefect.flow(
    log_prints=True,
    retries=settings.prefect.num_flow_retries,
    retry_delay_seconds=settings.prefect.flow_retry_delay_seconds,
)
def refresh_yearly_measurements(
    station_code: str | None = None,
    climatic_indicator_identifier: str | None = None,
):
    client = httpx.Client()
    all_created = []
    with sqlmodel.Session(db_engine) as db_session:
        if (
            len(
                db_climatic_indicators := _get_climatic_indicators(
                    db_session, climatic_indicator_identifier
                )
            )
            > 0
        ):
            if len(db_stations := _get_stations(db_session, station_code)) > 0:
                for db_station in db_stations:
                    to_create = []
                    to_wait_for = []
                    print(f"Processing station: {db_station.name!r}...")
                    for db_climatic_indicator in db_climatic_indicators:
                        print(
                            f"Processing climatic indicator: {db_climatic_indicator.identifier!r}..."
                        )
                        fut = harvest_yearly_measurements.submit(
                            client, db_session, db_station, db_climatic_indicator
                        )
                        to_wait_for.append(fut)
                    for future in to_wait_for:
                        to_create.extend(future.result())
                    print(f"creating {len(to_create)} new yearly measurements...")
                    created = database.create_many_yearly_measurements(
                        db_session, to_create
                    )
                    all_created.extend(created)
            else:
                print("There are no stations to process, skipping...")
        else:
            print("There are no variables to process, skipping...")
        prefect.artifacts.create_table_artifact(
            key="yearly-measurements-created",
            table=_build_created_measurements_table(all_created),
            description=f"# Created {len(all_created)} yearly measurements",
        )


def _get_stations(
    db_session: sqlmodel.Session, station_identifier: str | None = None
) -> list[observations.Station]:
    if station_identifier is not None:
        station = database.get_observation_station_by_identifier(
            db_session, station_identifier)
        result = [station] if station else []
    else:
        result = database.collect_all_observation_stations(db_session)
    return result


def _get_observation_series_configurations(
    db_session: sqlmodel.Session,
    observation_series_configuration_identifier: str | None = None,
) -> list[observations.ObservationSeriesConfiguration]:
    if observation_series_configuration_identifier is not None:
        series_conf = database.get_observation_series_configuration_by_identifier(
            db_session, observation_series_configuration_identifier
        )
        result = [series_conf] if series_conf else []
    else:
        result = database.collect_all_observation_series_configurations(db_session)
    return result


def _get_climatic_indicators(
    db_session: sqlmodel.Session, climatic_indicator_identifier: str | None = None
) -> list[climaticindicators.ClimaticIndicator]:
    if climatic_indicator_identifier is not None:
        climatic_indicator = database.get_climatic_indicator_by_identifier(
            db_session, climatic_indicator_identifier
        )
        result = [climatic_indicator] if climatic_indicator else []
    else:
        result = database.collect_all_climatic_indicators(db_session)
    return result


def _get_seasons(season_name: str | None = None) -> list[base.Season]:
    if season_name is not None:
        try:
            result = [base.Season(season_name.upper())]
        except ValueError:
            print(f"Invalid season name: {season_name!r}")
            result = []
    else:
        result = [s for s in base.Season]
    return result


def _get_months(month_index: int | None = None) -> list[int]:
    if month_index is not None:
        if 1 <= month_index <= 12:
            result = [month_index]
        else:
            print(f"Invalid month index: {month_index!r}")
            result = []
    else:
        result = list(range(1, 13))
    return result


def _build_created_measurements_table(
    measurements: Sequence[observations.MonthlyMeasurement]
    | Sequence[observations.SeasonalMeasurement]
    | Sequence[observations.YearlyMeasurement],
) -> list[dict]:
    aggregated_items = {}
    for measurement in measurements:
        station_identifier = f"{measurement.station.name} ({measurement.station.code})"
        station_items = aggregated_items.setdefault(station_identifier, {})
        climatic_indicator_items = station_items.setdefault(
            measurement.climatic_indicator.identifier, []
        )
        climatic_indicator_items.append(measurement)
    table_contents = []
    for station_identifier, station_items in aggregated_items.items():
        for climatic_indicator_identifier, measurement_items in station_items.items():
            table_contents.append(
                {
                    "station": station_identifier,
                    "climatic_indicator": climatic_indicator_identifier,
                    "number of new measurements": len(measurement_items),
                }
            )
    return table_contents


def build_monthly_measurement_id(
    measurement: Union[
        observations.MonthlyMeasurement, observations.MonthlyMeasurementCreate
    ],
) -> str:
    return "-".join(
        (
            str(measurement.station_id),
            str(measurement.climatic_indicator_id),
            measurement.date.strftime("%Y%m"),
        )
    )


def build_seasonal_measurement_id(
    measurement: Union[
        observations.SeasonalMeasurement, observations.SeasonalMeasurementCreate
    ],
) -> str:
    return "-".join(
        (
            str(measurement.station_id),
            str(measurement.climatic_indicator_id),
            str(measurement.year),
            measurement.season.value,
        )
    )


def build_yearly_measurement_id(
    measurement: Union[
        observations.YearlyMeasurement, observations.YearlyMeasurementCreate
    ],
) -> str:
    return "-".join(
        (
            str(measurement.station_id),
            str(measurement.climatic_indicator_id),
            str(measurement.year),
        )
    )


@prefect.task(
    retries=settings.prefect.num_task_retries,
    retry_delay_seconds=settings.prefect.task_retry_delay_seconds,
)
def refresh_stations_for_climatic_indicator(
    climatic_indicator_id: int, db_schema_name: str
):
    with sqlmodel.Session(db_engine) as db_session:
        climatic_indicator = database.get_climatic_indicator(
            db_session, climatic_indicator_id
        )
        return refresh_station_climatic_indicator_database_view(
            db_session, climatic_indicator, db_schema_name=db_schema_name
        )


@prefect.flow(
    log_prints=True,
    retries=settings.prefect.num_flow_retries,
    retry_delay_seconds=settings.prefect.flow_retry_delay_seconds,
)
def refresh_station_variables(
    climatic_indicator_identifier: str | None = None,
):
    with sqlmodel.Session(db_engine) as db_session:
        create_db_schema(db_session, settings.variable_stations_db_schema)
        climatic_indicator_ids = [
            ci.id
            for ci in _get_climatic_indicators(
                db_session, climatic_indicator_identifier
            )
        ]
    if len(climatic_indicator_ids) > 0:
        to_wait_on = []
        for climatic_indicator_id in climatic_indicator_ids:
            print(
                f"refreshing stations that have values for "
                f"climatic indicator with id: {climatic_indicator_id!r}..."
            )
            var_future = refresh_stations_for_climatic_indicator.submit(
                climatic_indicator_id,
                settings.variable_stations_db_schema,
            )
            to_wait_on.append(var_future)
        for future in to_wait_on:
            future.result()
    else:
        print("There are no climatic indicators to process, skipping...")
