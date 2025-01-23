from collections.abc import Iterable

import httpx
import sqlmodel
import prefect
import prefect.artifacts
import pyproj

from arpav_ppcv import (
    database,
    exceptions,
)
from arpav_ppcv.config import get_settings
from arpav_ppcv.observations_harvester import arpav as arpav_operations
from arpav_ppcv.observations_harvester import arpafvg as arpafvg_operations
from arpav_ppcv.operations import (
    create_db_schema,
    refresh_station_climatic_indicator_database_view,
)
from arpav_ppcv.schemas import (
    climaticindicators,
    observations,
)
from arpav_ppcv.schemas.static import (
    MeasureType,
    ObservationStationManager,
)

# this is a module global because we need to configure the prefect flow and
# task with values from it
_settings = get_settings()
_db_engine = database.get_engine(_settings)


@prefect.task(
    retries=_settings.prefect.num_task_retries,
    retry_delay_seconds=_settings.prefect.task_retry_delay_seconds,
)
def refresh_stations_for_climatic_indicator(
    climatic_indicator_id: int, db_schema_name: str
):
    with sqlmodel.Session(_db_engine) as db_session:
        climatic_indicator = database.get_climatic_indicator(
            db_session, climatic_indicator_id
        )
        return refresh_station_climatic_indicator_database_view(
            db_session, climatic_indicator, db_schema_name=db_schema_name
        )


@prefect.flow(
    log_prints=True,
    retries=_settings.prefect.num_flow_retries,
    retry_delay_seconds=_settings.prefect.flow_retry_delay_seconds,
)
def refresh_station_variables(
    climatic_indicator_identifier: str | None = None,
):
    with sqlmodel.Session(_db_engine) as db_session:
        create_db_schema(db_session, _settings.variable_stations_db_schema)
        to_wait_on = []
        for climatic_indicator in _get_climatic_indicators(
            db_session, climatic_indicator_identifier
        ):
            if climatic_indicator.measure_type == MeasureType.ABSOLUTE:
                print(
                    f"refreshing stations that have values for "
                    f"climatic indicator {climatic_indicator.identifier!r}..."
                )
                var_future = refresh_stations_for_climatic_indicator.submit(
                    climatic_indicator.id,
                    _settings.variable_stations_db_schema,
                )
                to_wait_on.append(var_future)
            else:
                print(
                    f"climatic indicator {climatic_indicator.identifier!r} does not "
                    f"specify {MeasureType.ABSOLUTE.value!r} as its measure type, "
                    f"skipping..."
                )
        for future in to_wait_on:
            future.result()


@prefect.task(
    retries=_settings.prefect.num_task_retries,
    retry_delay_seconds=_settings.prefect.task_retry_delay_seconds,
)
def harvest_stations(
    series_configuration_id: int,
) -> tuple[int, set[observations.ObservationStationCreate]]:
    with sqlmodel.Session(_db_engine) as session:
        series_configuration = database.get_observation_series_configuration(
            session, series_configuration_id
        )
        if series_configuration is None:
            raise exceptions.InvalidObservationSeriesConfigurationIdentifierError(
                f"Series configuration with id: {series_configuration_id!r} not found"
            )
        coord_converter = pyproj.Transformer.from_crs(
            pyproj.CRS("epsg:4258"), pyproj.CRS("epsg:4326"), always_xy=True
        ).transform
        stations = set()
        client = httpx.Client()
        for station_manager in series_configuration.station_managers:
            if station_manager == ObservationStationManager.ARPAV:
                retriever = arpav_operations.fetch_remote_stations(
                    client,
                    series_configuration,
                    observations_base_url=_settings.arpav_observations_base_url,
                )
                for raw_station in retriever:
                    stations.add(
                        arpav_operations.parse_station(raw_station, coord_converter)
                    )
            elif station_manager == ObservationStationManager.ARPAFVG:
                retriever = arpafvg_operations.fetch_remote_stations(
                    client,
                    series_configuration,
                    observations_base_url=_settings.arpafvg_observations_base_url,
                    auth_token=_settings.arpafvg_auth_token,
                )
                for raw_station in retriever:
                    stations.add(
                        arpafvg_operations.parse_station(raw_station, coord_converter)
                    )
            else:
                raise NotImplementedError(
                    f"Observation stations managed by {station_manager} are not "
                    f"implemented."
                )
        return series_configuration_id, stations


@prefect.task(
    retries=_settings.prefect.num_task_retries,
    retry_delay_seconds=_settings.prefect.task_retry_delay_seconds,
)
def find_new_stations(
    candidate_stations: Iterable[observations.ObservationStationCreate],
) -> list[observations.ObservationStationCreate]:
    with sqlmodel.Session(_db_engine) as session:
        db_stations = database.collect_all_observation_stations(session)
        existing_stations = {(s.managed_by, s.code): s for s in db_stations}
        possibly_new_stations = {(s.managed_by, s.code): s for s in candidate_stations}
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
                possibly_new_stations.get(
                    (existing_station.managed_by, existing_station.code)
                )
                is None
            ):
                print(
                    f"Station {existing_station.code} is not "
                    f"found on the remote. Maybe it can be deleted? The system does not "
                    f"delete stations so please check manually if this should be deleted "
                    f"or not"
                )
        return to_create


@prefect.flow(
    log_prints=True,
    retries=_settings.prefect.num_flow_retries,
    retry_delay_seconds=_settings.prefect.flow_retry_delay_seconds,
)
def refresh_stations(observation_series_configuration_identifier: str | None = None):
    with sqlmodel.Session(_db_engine) as session:
        db_series_configurations = _get_observation_series_configurations(
            session, observation_series_configuration_identifier
        )
        if len(db_series_configurations) > 0:
            all_harvested_stations = {}
            to_wait_on = []
            for series_conf in db_series_configurations:
                print(
                    f"refreshing stations that are part of series "
                    f"{series_conf.identifier!r}..."
                )
                fut = harvest_stations.submit(series_conf.id)
                to_wait_on.append(fut)
            for future in to_wait_on:
                series_id, series_harvested_stations = future.result()
                all_harvested_stations[series_id] = series_harvested_stations

            candidate_stations = set()
            for harvested_stations in all_harvested_stations.values():
                candidate_stations.update(harvested_stations)
            to_create = find_new_stations(candidate_stations)
            if len(to_create) > 0:
                print(f"Found {len(to_create)} new stations. Creating them now...")
                for s in to_create:
                    print(f"- ({s.code}) {s.name}")
                created = database.create_many_observation_stations(session, to_create)
            else:
                created = []
                print("No new stations found.")
            prefect.artifacts.create_table_artifact(
                key="stations-created",
                table=[
                    {"id": str(s.id), "code": s.code, "name": s.name} for s in created
                ],
                description=f"# Created {len(created)} stations",
            )
            # now we need to associate stations with their respective climatic indicator
            for osc_id, series_harvested_stations in all_harvested_stations.items():
                observation_series_configuration = (
                    database.get_observation_series_configuration(session, osc_id)
                )
                if observation_series_configuration is not None:
                    for harvested_station in series_harvested_stations:
                        # by now all harvested stations should be present in the DB
                        existing_db_station = database.get_observation_station_by_code(
                            session, harvested_station.code
                        )
                        if existing_db_station is not None:
                            new_indicator_ids = set(
                                ci.id for ci in existing_db_station.climatic_indicators
                            )
                            new_indicator_ids.add(
                                observation_series_configuration.climatic_indicator_id
                            )
                            database.update_observation_station(
                                session,
                                existing_db_station,
                                observations.ObservationStationUpdate(
                                    climatic_indicators=list(new_indicator_ids),
                                ),
                            )
                else:
                    print(
                        f"Observation series configuration with id {osc_id} not found, "
                        f"ignoring..."
                    )

        else:
            print("There are no variables to process, skipping...")


@prefect.flow(
    log_prints=True,
    retries=_settings.prefect.num_flow_retries,
    retry_delay_seconds=_settings.prefect.flow_retry_delay_seconds,
)
def refresh_measurements(
    station_code: str | None = None,
    observation_series_configuration_identifier: str | None = None,
):
    to_wait_on = []
    to_filter_for_new_measurements = {}
    with sqlmodel.Session(_db_engine) as db_session:
        stations_to_process = _get_stations(db_session, station_code)
        series_confs_to_process = _get_observation_series_configurations(
            db_session, observation_series_configuration_identifier
        )
        print(f"{[s.code for s in stations_to_process]=}")
        for station in stations_to_process:
            to_filter_for_new_measurements.setdefault(station.code, [])
            for series_configuration in series_confs_to_process:
                # is this station associated with this data series' climatic indicator?
                if series_configuration.climatic_indicator.id in [
                    ci.id for ci in station.climatic_indicators
                ]:
                    if station.managed_by == ObservationStationManager.ARPAV:
                        fut = harvest_arpav_station_measurements.submit(
                            station.id, series_configuration.id
                        )
                        to_wait_on.append(fut)
                    elif station.managed_by == ObservationStationManager.ARPAFVG:
                        fut = harvest_arpafvg_station_measurements.submit(
                            station.id, series_configuration.id
                        )
                        to_wait_on.append(fut)
                    else:
                        raise NotImplementedError(
                            f"Observation stations managed by {station.managed_by} "
                            f"are not implemented."
                        )
                else:
                    print(
                        f"Station {station.code!r} is not associated with the "
                        f"{series_configuration.climatic_indicator.identifier!r} "
                        f"climatic indicator"
                    )

        for future in to_wait_on:
            station_measurements_to_create: list[
                observations.ObservationMeasurementCreate
            ] = future.result()
            try:
                first_harvested_measurement = station_measurements_to_create[0]
                to_filter_for_new_measurements[
                    first_harvested_measurement.observation_station_id
                ].extend(station_measurements_to_create)
            except IndexError:
                pass  # received an empty list, ignore

        print(f"{to_filter_for_new_measurements=}")
        all_created = []
        for (
            station_code,
            harvested_measurements,
        ) in to_filter_for_new_measurements.items():
            station = database.get_observation_station_by_code(db_session, station_code)
            to_create = database.find_new_station_measurements(
                db_session,
                station_id=station.id,
                candidates=harvested_measurements,
            )
            if len(to_create) > 0:
                print(
                    f"Found {len(to_create)} new measurements for station "
                    f"{station.code!r}. Creating them now..."
                )
                created = database.create_many_observation_measurements(
                    db_session, to_create
                )
                all_created.extend(created)
            else:
                print(f"No new measurements found for station {station.code!r}.")

        prefect.artifacts.create_table_artifact(
            key="measurements-created",
            table=[
                {
                    "id": str(m.id),
                    "station": m.observation_station.code,
                    "climatic_indicator": m.climatic_indicator.identifier,
                    "date": m.date.strftime("%Y-%m-%d"),
                    "value": m.value,
                }
                for m in all_created
            ],
            description=f"# Created {len(all_created)} measurements",
        )


@prefect.task(
    log_prints=True,
    retries=_settings.prefect.num_task_retries,
    retry_delay_seconds=_settings.prefect.task_retry_delay_seconds,
)
def harvest_arpafvg_station_measurements(
    station_id: int,
    series_configuration_id: int,
) -> list[observations.ObservationMeasurementCreate]:
    client = httpx.Client()
    with sqlmodel.Session(_db_engine) as session:
        station = database.get_observation_station(session, station_id)
        if station is None:
            raise exceptions.InvalidObservationStationIdError(
                f"Station {station_id!r} does not exist."
            )
        series_configuration = database.get_observation_series_configuration(
            session, series_configuration_id
        )
        if series_configuration is None:
            raise exceptions.InvalidObservationSeriesConfigurationIdError(
                f"Series configuration {series_configuration_id!r} does not exist."
            )
        harvested_measurements = []
        raw_measurement_gen = arpafvg_operations.fetch_station_measurements(
            client,
            station,
            series_configuration,
            _settings.arpafvg_observations_base_url,
            _settings.arpafvg_auth_token,
        )
        for year_period, raw_measurement in raw_measurement_gen:
            harvested_measurements.append(
                arpafvg_operations.parse_measurement(
                    raw_measurement,
                    year_period,
                    station,
                    series_configuration.climatic_indicator,
                )
            )
        print(f"harvested_measurements={harvested_measurements}")
        return harvested_measurements


@prefect.task(
    retries=_settings.prefect.num_task_retries,
    retry_delay_seconds=_settings.prefect.task_retry_delay_seconds,
)
def harvest_arpav_station_measurements(
    station_id: int,
    series_configuration_id: int,
) -> list[observations.ObservationMeasurementCreate]:
    client = httpx.Client()
    with sqlmodel.Session(_db_engine) as session:
        station = database.get_observation_station(session, station_id)
        if station is None:
            raise exceptions.InvalidObservationStationIdError(
                f"Station {station_id!r} does not exist."
            )
        series_configuration = database.get_observation_series_configuration(
            session, series_configuration_id
        )
        if series_configuration is None:
            raise exceptions.InvalidObservationSeriesConfigurationIdError(
                f"Series configuration {series_configuration_id!r} does not exist."
            )
        harvested_measurements = []
        raw_measurement_gen = arpav_operations.fetch_station_measurements(
            client, station, series_configuration, _settings.arpav_observations_base_url
        )
        for year_period, raw_measurement in raw_measurement_gen:
            harvested_measurements.append(
                arpav_operations.parse_measurement(
                    raw_measurement,
                    year_period,
                    station,
                    series_configuration.climatic_indicator,
                )
            )
        return harvested_measurements


def _get_stations(
    db_session: sqlmodel.Session, station_code: str | None = None
) -> list[observations.ObservationStation]:
    if station_code is not None:
        station = database.get_observation_station_by_code(db_session, station_code)
        if station is not None:
            result = [station]
        else:
            raise exceptions.InvalidObservationStationCodeError(
                f"station with code {station_code!r} not found"
            )
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
        if series_conf is not None:
            result = [series_conf]
        else:
            raise exceptions.InvalidObservationSeriesConfigurationIdentifierError(
                f"observation series configuration identifier "
                f"{observation_series_configuration_identifier!r} not found"
            )
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
