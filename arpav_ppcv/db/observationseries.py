from typing import (
    Optional,
    Sequence,
)

import sqlalchemy
import sqlmodel

from .. import exceptions
from ..schemas.observations import (
    ObservationMeasurement,
    ObservationMeasurementCreate,
    ObservationMeasurementUpdate,
    ObservationSeriesConfiguration,
    ObservationSeriesConfigurationCreate,
    ObservationSeriesConfigurationUpdate,
)
from ..schemas.static import (
    MeasurementAggregationType,
    ObservationStationManager,
)

from .base import (
    get_total_num_records,
)
from .climaticindicators import get_climatic_indicator_by_identifier
from .observationstations import get_observation_station


def get_observation_measurement(
    session: sqlmodel.Session, observation_measurement_id: int
) -> Optional[ObservationMeasurement]:
    return session.get(ObservationMeasurement, observation_measurement_id)


def list_observation_measurements(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    observation_station_id_filter: Optional[int] = None,
    climatic_indicator_id_filter: Optional[int] = None,
    aggregation_type_filter: Optional[MeasurementAggregationType] = None,
    include_total: bool = False,
) -> tuple[Sequence[ObservationMeasurement], Optional[int]]:
    """List existing observation measurements."""
    statement = sqlmodel.select(ObservationMeasurement).order_by(
        ObservationMeasurement.date  # noqa
    )
    if observation_station_id_filter is not None:
        statement = statement.where(
            ObservationMeasurement.observation_station_id  # noqa
            == observation_station_id_filter
        )
    if climatic_indicator_id_filter is not None:
        statement = statement.where(
            ObservationMeasurement.climatic_indicator_id  # noqa
            == climatic_indicator_id_filter
        )
    if aggregation_type_filter is not None:
        statement = statement.where(
            ObservationMeasurement.measurement_aggregation_type  # noqa
            == aggregation_type_filter.name
        )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_observation_measurements(
    session: sqlmodel.Session,
    *,
    observation_station_id_filter: Optional[int] = None,
    climatic_indicator_id_filter: Optional[int] = None,
    aggregation_type_filter: Optional[MeasurementAggregationType] = None,
) -> Sequence[ObservationMeasurement]:
    _, num_total = list_observation_measurements(
        session,
        limit=1,
        observation_station_id_filter=observation_station_id_filter,
        climatic_indicator_id_filter=climatic_indicator_id_filter,
        aggregation_type_filter=aggregation_type_filter,
        include_total=True,
    )
    result, _ = list_observation_measurements(
        session,
        limit=num_total,
        observation_station_id_filter=observation_station_id_filter,
        climatic_indicator_id_filter=climatic_indicator_id_filter,
        aggregation_type_filter=aggregation_type_filter,
        include_total=False,
    )
    return result


def create_observation_measurement(
    session: sqlmodel.Session,
    observation_measurement_create: ObservationMeasurementUpdate,
) -> ObservationMeasurement:
    """Create a new observation measurement."""
    db_measurement = ObservationMeasurement(
        **observation_measurement_create.model_dump()
    )
    session.add(db_measurement)
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        session.refresh(db_measurement)
        return db_measurement


def create_many_observation_measurements(
    session: sqlmodel.Session,
    observation_measurements_to_create: Sequence[
        ObservationMeasurementCreate
    ],
) -> list[ObservationMeasurement]:
    """Create several observation measurements."""
    db_records = []
    for measurement_create in observation_measurements_to_create:
        db_measurement = ObservationMeasurement(
            observation_station_id=measurement_create.observation_station_id,
            climatic_indicator_id=measurement_create.climatic_indicator_id,
            value=measurement_create.value,
            date=measurement_create.date,
            measurement_aggregation_type=measurement_create.measurement_aggregation_type,
        )
        db_records.append(db_measurement)
        session.add(db_measurement)
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        for db_record in db_records:
            session.refresh(db_record)
        return db_records


def delete_observation_measurement(
    session: sqlmodel.Session, observation_measurement_id: int
) -> None:
    """Delete an observation measurement."""
    if (
            db_measurement := get_observation_measurement(
                session, observation_measurement_id
            )
    ) is not None:
        session.delete(db_measurement)
        session.commit()
    else:
        raise RuntimeError("Observation measurement not found")


def get_observation_series_configuration(
    session: sqlmodel.Session, observation_series_configuration_id: int
) -> Optional[ObservationSeriesConfiguration]:
    return session.get(
        ObservationSeriesConfiguration, observation_series_configuration_id
    )


def get_observation_series_configuration_by_identifier(
    session: sqlmodel.Session, identifier: str
) -> Optional[ObservationSeriesConfiguration]:
    parts = identifier.split("-")
    climatic_indicator_identifier = "-".join(parts[:3])
    climatic_indicator = get_climatic_indicator_by_identifier(
        session, climatic_indicator_identifier
    )
    if climatic_indicator is None:
        raise exceptions.InvalidObservationSeriesConfigurationIdentifierError(
            f"climatic indicator {climatic_indicator_identifier} does not exist"
        )
    raw_station_managers, raw_measurement_aggregation = parts[3:5]
    managers = [
        ObservationStationManager(m) for m in raw_station_managers.split(":")
    ]
    measurement_aggregation_type = MeasurementAggregationType(
        raw_measurement_aggregation
    )
    statement = sqlmodel.select(ObservationSeriesConfiguration).where(
        ObservationSeriesConfiguration.climatic_indicator_id  # noqa
        == climatic_indicator.id,
        ObservationSeriesConfiguration.measurement_aggregation_type  # noqa
        == measurement_aggregation_type,
        ObservationSeriesConfiguration.station_managers == managers,  # noqa
        )
    return session.exec(statement).first()  # noqa


def list_observation_series_configurations(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
) -> tuple[Sequence[ObservationSeriesConfiguration], Optional[int]]:
    """List existing observation series configurations."""
    statement = sqlmodel.select(ObservationSeriesConfiguration).order_by(
        ObservationSeriesConfiguration.id  # noqa
    )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_observation_series_configurations(
    session: sqlmodel.Session,
) -> Sequence[ObservationSeriesConfiguration]:
    """Collect all observation series configurations."""
    _, num_total = list_observation_series_configurations(
        session,
        limit=1,
        include_total=True,
    )
    result, _ = list_observation_series_configurations(
        session,
        limit=num_total,
        include_total=False,
    )
    return result


def create_observation_series_configuration(
    session: sqlmodel.Session,
    observation_series_configuration_create: ObservationSeriesConfigurationCreate,
) -> ObservationSeriesConfiguration:
    """Create a new observation series configuration."""
    db_series_conf = ObservationSeriesConfiguration(
        **observation_series_configuration_create.model_dump(),
    )
    session.add(db_series_conf)
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        session.refresh(db_series_conf)
        return db_series_conf


def update_observation_series_configuration(
    session: sqlmodel.Session,
    db_observation_series_configuration: ObservationSeriesConfiguration,
    observation_series_configuration_update: ObservationSeriesConfigurationUpdate,
) -> ObservationSeriesConfiguration:
    """Update an observation series configuration."""
    data = observation_series_configuration_update.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_observation_series_configuration, key, value)
    session.add(db_observation_series_configuration)
    session.commit()
    session.refresh(db_observation_series_configuration)
    return db_observation_series_configuration


def delete_observation_series_configuration(
    session: sqlmodel.Session, observation_series_configuration_id: int
) -> None:
    """Delete an observation series configuration."""
    db_item = get_observation_station(session, observation_series_configuration_id)
    if db_item is not None:
        session.delete(db_item)
        session.commit()
    else:
        raise RuntimeError("Observation series configuration not found")


def find_new_station_measurements(
    session: sqlmodel.Session,
    *,
    station_id: int,
    candidates: Sequence[ObservationMeasurementCreate],
) -> list[ObservationMeasurementCreate]:
    """Filter the list of candidate measurements, leaving only those that are new."""
    existing_measurements = collect_all_observation_measurements(
        session, observation_station_id_filter=station_id
    )
    to_drop = []
    for candidate in candidates:
        for existing in existing_measurements:
            if candidate.climatic_indicator_id == existing.climatic_indicator_id:
                if candidate.date == existing.date:
                    to_drop.append(candidate.identifier)
    return [m for m in candidates if m.identifier not in to_drop]
