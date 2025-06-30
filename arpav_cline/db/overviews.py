from typing import (
    Optional,
    Sequence,
)
import sqlmodel

from .. import exceptions
from ..schemas.overviews import (
    ForecastOverviewSeriesConfiguration,
    ForecastOverviewSeriesConfigurationCreate,
    ForecastOverviewSeriesConfigurationUpdate,
    ForecastOverviewSeriesInternal,
    ObservationOverviewSeriesConfiguration,
    ObservationOverviewSeriesConfigurationCreate,
    ObservationOverviewSeriesConfigurationUpdate,
    ObservationOverviewSeriesInternal,
)
from ..schemas.static import (
    DataCategory,
)
from .base import get_total_num_records
from .climaticindicators import get_climatic_indicator_by_identifier


def list_forecast_overview_series_configurations(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
) -> tuple[Sequence[ForecastOverviewSeriesConfiguration], Optional[int]]:
    """List existing forecast overview series configurations."""
    statement = sqlmodel.select(ForecastOverviewSeriesConfiguration).order_by(
        ForecastOverviewSeriesConfiguration.id  # noqa
    )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_forecast_overview_series_configurations(
    session: sqlmodel.Session,
) -> Sequence[ForecastOverviewSeriesConfiguration]:
    _, num_total = list_forecast_overview_series_configurations(
        session,
        limit=1,
        include_total=True,
    )
    result, _ = list_forecast_overview_series_configurations(
        session,
        limit=num_total,
        include_total=False,
    )
    return result


def get_forecast_overview_series_configuration(
    session: sqlmodel.Session,
    forecast_overview_series_configuration_id: int,
) -> Optional[ForecastOverviewSeriesConfiguration]:
    return session.get(
        ForecastOverviewSeriesConfiguration,
        forecast_overview_series_configuration_id,
    )


def get_forecast_overview_series_configuration_by_identifier(
    session: sqlmodel.Session,
    forecast_overview_series_configuration_identifier: str,
) -> Optional[ForecastOverviewSeriesConfiguration]:
    parts = forecast_overview_series_configuration_identifier.split("-")
    if parts[0] == "overview" and parts[1] == DataCategory.FORECAST.value:
        climatic_indicator_identifier = "-".join(parts[2:])
        climatic_indicator = get_climatic_indicator_by_identifier(
            session, climatic_indicator_identifier
        )
        if climatic_indicator is not None:
            statement = sqlmodel.select(ForecastOverviewSeriesConfiguration).where(
                ForecastOverviewSeriesConfiguration.climatic_indicator_id  # noqa
                == climatic_indicator.id,
            )
            result = session.exec(statement).first()  # noqa
        else:
            raise exceptions.InvalidOverviewSeriesConfigurationIdentifierError(
                f"Could not find a climatic indicator with identifier "
                f"{climatic_indicator_identifier!r}"
            )
    else:
        raise exceptions.InvalidOverviewSeriesConfigurationIdentifierError(
            "invalid forecast overview series configuration identifier"
        )
    return result


def create_forecast_overview_series_configuration(
    session: sqlmodel.Session,
    forecast_overview_series_configuration_create: ForecastOverviewSeriesConfigurationCreate,
) -> ForecastOverviewSeriesConfiguration:
    db_overview_coverage_configuration = ForecastOverviewSeriesConfiguration(
        **forecast_overview_series_configuration_create.model_dump()
    )
    session.add(db_overview_coverage_configuration)
    session.commit()
    session.refresh(db_overview_coverage_configuration)
    return db_overview_coverage_configuration


def update_forecast_overview_series_configuration(
    session: sqlmodel.Session,
    db_forecast_overview_series_configuration: ForecastOverviewSeriesConfiguration,
    forecast_overview_series_configuration_update: ForecastOverviewSeriesConfigurationUpdate,
) -> ForecastOverviewSeriesConfiguration:
    """Update a forecast overview series configuration."""
    data_ = forecast_overview_series_configuration_update.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )
    for key, value in data_.items():
        setattr(db_forecast_overview_series_configuration, key, value)
    session.add(db_forecast_overview_series_configuration)
    session.commit()
    session.refresh(db_forecast_overview_series_configuration)
    return db_forecast_overview_series_configuration


def delete_forecast_overview_series_configuration(
    session: sqlmodel.Session, forecast_overview_series_configuration_id: int
) -> None:
    db_item = get_forecast_overview_series_configuration(
        session, forecast_overview_series_configuration_id
    )
    if db_item is not None:
        session.delete(db_item)
        session.commit()
    else:
        raise RuntimeError("Forecast overview series configuration not found")


def list_observation_overview_series_configurations(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
) -> tuple[Sequence[ObservationOverviewSeriesConfiguration], Optional[int]]:
    """List existing observation overview series configurations."""
    statement = sqlmodel.select(ObservationOverviewSeriesConfiguration).order_by(
        ObservationOverviewSeriesConfiguration.id
    )  # noqa
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_observation_overview_series_configurations(
    session: sqlmodel.Session,
) -> Sequence[ObservationOverviewSeriesConfiguration]:
    _, num_total = list_observation_overview_series_configurations(
        session,
        limit=1,
        include_total=True,
    )
    result, _ = list_observation_overview_series_configurations(
        session,
        limit=num_total,
        include_total=False,
    )
    return result


def get_observation_overview_series_configuration(
    session: sqlmodel.Session,
    observation_overview_series_configuration_id: int,
) -> Optional[ObservationOverviewSeriesConfiguration]:
    return session.get(
        ObservationOverviewSeriesConfiguration,
        observation_overview_series_configuration_id,
    )


def get_observation_overview_series_configuration_by_identifier(
    session: sqlmodel.Session,
    observation_overview_series_configuration_identifier: str,
) -> Optional[ForecastOverviewSeriesConfiguration]:
    parts = observation_overview_series_configuration_identifier.split("-")
    if parts[0] == "overview" and parts[1] == DataCategory.HISTORICAL.value:
        climatic_indicator_identifier = "-".join(parts[2:])
        climatic_indicator = get_climatic_indicator_by_identifier(
            session, climatic_indicator_identifier
        )
        if climatic_indicator is not None:
            statement = sqlmodel.select(ObservationOverviewSeriesConfiguration).where(
                ObservationOverviewSeriesConfiguration.climatic_indicator_id  # noqa
                == climatic_indicator.id,
            )
            result = session.exec(statement).first()  # noqa
        else:
            raise exceptions.InvalidOverviewSeriesConfigurationIdentifierError(
                f"Could not find a climatic indicator with identifier "
                f"{climatic_indicator_identifier!r}"
            )
    else:
        raise exceptions.InvalidOverviewSeriesConfigurationIdentifierError(
            "invalid forecast overview series configuration identifier"
        )
    return result


def create_observation_overview_series_configuration(
    session: sqlmodel.Session,
    observation_overview_series_configuration_create: ObservationOverviewSeriesConfigurationCreate,
) -> ObservationOverviewSeriesConfiguration:
    db_overview_coverage_configuration = ObservationOverviewSeriesConfiguration(
        **observation_overview_series_configuration_create.model_dump()
    )
    session.add(db_overview_coverage_configuration)
    session.commit()
    session.refresh(db_overview_coverage_configuration)
    return db_overview_coverage_configuration


def update_observation_overview_series_configuration(
    session: sqlmodel.Session,
    db_observation_overview_series_configuration: ObservationOverviewSeriesConfiguration,
    observation_overview_series_configuration_update: ObservationOverviewSeriesConfigurationUpdate,
) -> ObservationOverviewSeriesConfiguration:
    """Update an observation overview series configuration."""
    data_ = observation_overview_series_configuration_update.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )
    for key, value in data_.items():
        setattr(db_observation_overview_series_configuration, key, value)
    session.add(db_observation_overview_series_configuration)
    session.commit()
    session.refresh(db_observation_overview_series_configuration)
    return db_observation_overview_series_configuration


def delete_observation_overview_series_configuration(
    session: sqlmodel.Session, observation_overview_series_configuration_id: int
) -> None:
    db_item = get_observation_overview_series_configuration(
        session, observation_overview_series_configuration_id
    )
    if db_item is not None:
        session.delete(db_item)
        session.commit()
    else:
        raise RuntimeError("Observation overview series configuration not found")


def generate_forecast_overview_series_from_configuration(
    forecast_overview_series_configuration: ForecastOverviewSeriesConfiguration,
) -> list[ForecastOverviewSeriesInternal]:
    result = []
    for scenario in forecast_overview_series_configuration.scenarios:
        result.append(
            ForecastOverviewSeriesInternal(
                configuration=forecast_overview_series_configuration,
                scenario=scenario,
            )
        )
    return result


def generate_observation_overview_series_from_configuration(
    observation_overview_series_configuration: ObservationOverviewSeriesConfiguration,
) -> ObservationOverviewSeriesInternal:
    return ObservationOverviewSeriesInternal(
        configuration=observation_overview_series_configuration
    )
