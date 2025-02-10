from typing import (
    Optional,
    Sequence,
)

import sqlalchemy
import sqlmodel

from .. import exceptions
from ..schemas.climaticindicators import (
    ClimaticIndicator,
    ClimaticIndicatorCreate,
    ClimaticIndicatorUpdate,
)
from ..schemas.coverages import ForecastModelClimaticIndicatorLink
from ..schemas.observations import (
    ClimaticIndicatorObservationName,
)
from ..schemas.static import (
    AggregationPeriod,
    MeasureType,
)
from .base import (
    add_substring_filter,
    get_total_num_records,
)


def get_climatic_indicator(
    session: sqlmodel.Session, climatic_indicator_id: int
) -> Optional[ClimaticIndicator]:
    return session.get(ClimaticIndicator, climatic_indicator_id)


def get_climatic_indicator_by_identifier(
    session: sqlmodel.Session, climatic_indicator_identifier: str
) -> Optional[ClimaticIndicator]:
    name, raw_measure, raw_aggregation_period = climatic_indicator_identifier.split("-")
    try:
        measure_type = MeasureType(raw_measure)
        aggregation_period = AggregationPeriod(raw_aggregation_period)
    except ValueError as err:
        raise exceptions.InvalidClimaticIndicatorIdentifierError(
            f"Invalid measure type ({raw_measure!r}) or "
            f"aggregation period ({raw_aggregation_period!r})"
        ) from err
    else:
        statement = sqlmodel.select(ClimaticIndicator).where(
            ClimaticIndicator.name == name,  # noqa
            ClimaticIndicator.measure_type == measure_type,  # noqa
            ClimaticIndicator.aggregation_period == aggregation_period,  # noqa
            )
        return session.exec(statement).first()  # noqa


def list_climatic_indicators(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    name_filter: str | None = None,
    measure_type_filter: str | None = None,
    aggregation_period_filter: str | None = None,
) -> tuple[Sequence[ClimaticIndicator], Optional[int]]:
    """List existing climatic indicators."""
    statement = sqlmodel.select(ClimaticIndicator).order_by(
        ClimaticIndicator.sort_order,  # noqa
        ClimaticIndicator.name,  # noqa
        ClimaticIndicator.aggregation_period,  # noqa
        ClimaticIndicator.measure_type,  # noqa
    )
    if name_filter is not None:
        statement = add_substring_filter(
            statement, name_filter, ClimaticIndicator.name  # noqa
        )
    if measure_type_filter is not None:
        statement = add_substring_filter(
            statement,
            measure_type_filter,
            ClimaticIndicator.measure_type,  # noqa
        )
    if aggregation_period_filter is not None:
        statement = add_substring_filter(
            statement,
            aggregation_period_filter,
            ClimaticIndicator.aggregation_period,  # noqa
        )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_climatic_indicators(
    session: sqlmodel.Session,
    name_filter: Optional[str] = None,
    measure_type_filter: str | None = None,
    aggregation_period_filter: str | None = None,
) -> Sequence[ClimaticIndicator]:
    _, num_total = list_climatic_indicators(
        session,
        limit=1,
        include_total=True,
        name_filter=name_filter,
        measure_type_filter=measure_type_filter,
        aggregation_period_filter=aggregation_period_filter,
    )
    result, _ = list_climatic_indicators(
        session,
        limit=num_total,
        include_total=False,
        name_filter=name_filter,
        measure_type_filter=measure_type_filter,
        aggregation_period_filter=aggregation_period_filter,
    )
    return result


def create_climatic_indicator(
    session: sqlmodel.Session,
    climatic_indicator_create: ClimaticIndicatorCreate,
) -> ClimaticIndicator:
    """Create a new climatic indicator."""
    to_refresh = []
    db_climatic_indicator = ClimaticIndicator(
        **climatic_indicator_create.model_dump(
            exclude={
                "observation_names",
                "forecast_models",
            }
        ),
    )
    to_refresh.append(db_climatic_indicator)
    for obs_name in climatic_indicator_create.observation_names:
        db_obs_name = ClimaticIndicatorObservationName(
            station_manager=obs_name.observation_station_manager,
            indicator_observation_name=obs_name.indicator_observation_name,
        )
        db_climatic_indicator.observation_names.append(db_obs_name)
        to_refresh.append(db_obs_name)
    for forecast_model_info in climatic_indicator_create.forecast_models:
        db_forecast_model_climatic_indicator_link = ForecastModelClimaticIndicatorLink(
            forecast_model_id=forecast_model_info.forecast_model_id,
            thredds_url_base_path=forecast_model_info.thredds_url_base_path,
            thredds_url_uncertainties_base_path=forecast_model_info.thredds_url_uncertainties_base_path,
        )
        db_climatic_indicator.forecast_model_links.append(
            db_forecast_model_climatic_indicator_link
        )
        to_refresh.append(db_forecast_model_climatic_indicator_link)
    session.add(db_climatic_indicator)
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        for item in to_refresh:
            session.refresh(item)
        return db_climatic_indicator


def update_climatic_indicator(
    session: sqlmodel.Session,
    db_climatic_indicator: ClimaticIndicator,
    climatic_indicator_update: ClimaticIndicatorUpdate,
) -> ClimaticIndicator:
    """Update a climatic indicator."""
    to_refresh = []
    requested_obs_names = {
        "-".join(
            (str(db_climatic_indicator.id), ron.observation_station_manager.value)
        ): ron
        for ron in climatic_indicator_update.observation_names
    }
    existing_obs_names = {
        "-".join((str(db_climatic_indicator.id), ron.station_manager.value)): ron
        for ron in db_climatic_indicator.observation_names
    }
    for existing_key, existing_obs_name in existing_obs_names.items():
        has_been_requested_to_remove = existing_key not in requested_obs_names
        if has_been_requested_to_remove:
            session.delete(existing_obs_name)
    for requested_key, requested_obs_name in requested_obs_names.items():
        if requested_key not in existing_obs_names:  # need to create this one
            db_observation_name = ClimaticIndicatorObservationName(
                station_manager=requested_obs_name.observation_station_manager,
                indicator_observation_name=requested_obs_name.indicator_observation_name,
            )
            db_climatic_indicator.observation_names.append(db_observation_name)
        else:  # already exists, just update
            existing_db_observation_name = existing_obs_names[requested_key]
            existing_db_observation_name.indicator_observation_name = (
                requested_obs_name.indicator_observation_name
            )
            session.add(existing_db_observation_name)
            to_refresh.append(existing_db_observation_name)
    requested_forecast_model_links = {
        fm.forecast_model_id: fm for fm in climatic_indicator_update.forecast_models
    }
    existing_forecast_model_links = {
        db_fm.forecast_model_id: db_fm
        for db_fm in db_climatic_indicator.forecast_model_links
    }
    for existing_fm_id, existing_fm_link in existing_forecast_model_links.items():
        has_been_requested_to_remove = (
                existing_fm_id not in requested_forecast_model_links
        )
        if has_been_requested_to_remove:
            session.delete(existing_fm_link)
    for requested_fm_id, requested_fm in requested_forecast_model_links:
        if (
                requested_fm_id not in existing_forecast_model_links
        ):  # need to create this one
            db_fm_link = ForecastModelClimaticIndicatorLink(
                forecast_model_id=requested_fm_id,
                climatic_indicator_id=db_climatic_indicator.id,
                thredds_url_base_path=requested_fm.thredds_url_base_path,
                thredds_url_uncertainties_base_path=requested_fm.thredds_url_uncertainties_base_path,
            )
            db_climatic_indicator.forecast_model_links.append(db_fm_link)
        else:  # already exists, just update
            existing_fm_link = existing_forecast_model_links[requested_fm_id]
            existing_fm_link.thredds_url_base_path = requested_fm.thredds_url_base_path
            session.add(existing_fm_link)
            to_refresh.append(existing_fm_link)
    data_ = climatic_indicator_update.model_dump(
        exclude_unset=True,
        exclude={
            "observation_names",
            "forecast_models",
        },
    )
    for key, value in data_.items():
        setattr(db_climatic_indicator, key, value)
    session.add(db_climatic_indicator)
    to_refresh.append(db_climatic_indicator)
    session.commit()
    for item in to_refresh:
        session.refresh(item)
    return db_climatic_indicator


def delete_climatic_indicator(
    session: sqlmodel.Session, climatic_indicator_id: int
) -> None:
    """Delete a climatic indicator."""
    db_indicator = get_climatic_indicator(session, climatic_indicator_id)
    if db_indicator is not None:
        session.delete(db_indicator)
        session.commit()
    else:
        raise exceptions.InvalidClimaticIndicatorIdError()
