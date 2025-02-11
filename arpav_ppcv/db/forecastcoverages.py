import datetime as dt
import itertools
import logging
from typing import (
    Optional,
    Sequence,
)

import geohashr
import shapely
import sqlalchemy
import sqlmodel

from .. import exceptions
from ..schemas.base import SpatialRegion
from ..schemas.climaticindicators import (
    ClimaticIndicator,
)
from ..schemas.coverages import (
    ForecastCoverageConfiguration,
    ForecastCoverageConfigurationCreate,
    ForecastCoverageConfigurationUpdate,
    ForecastCoverageConfigurationForecastModelLink,
    ForecastCoverageConfigurationForecastTimeWindowLink,
    ForecastCoverageConfigurationObservationSeriesConfigurationLink,
    ForecastCoverageInternal,
    ForecastModel,
    ForecastModelCreate,
    ForecastModelUpdate,
    ForecastTimeWindow,
    ForecastTimeWindowCreate,
    ForecastTimeWindowUpdate,
    LegacyConfParamFilterValues,
)
from ..schemas.dataseries import ForecastDataSeries
from ..schemas.static import (
    CoverageTimeSeriesProcessingMethod,
    DataCategory,
    DatasetType,
    ForecastScenario,
    ForecastYearPeriod,
)

from .base import (
    add_substring_filter,
    get_total_num_records,
)
from .climaticindicators import get_climatic_indicator_by_identifier
from .observationseries import get_observation_series_configuration
from .spatialregions import get_spatial_region_by_name

logger = logging.getLogger(__name__)


def list_forecast_coverage_configurations(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    climatic_indicator_name_filter: Optional[str] = None,
    climatic_indicator_filter: Optional[ClimaticIndicator] = None,
) -> tuple[Sequence[ForecastCoverageConfiguration], Optional[int]]:
    """List existing forecast coverage configurations."""
    statement = sqlmodel.select(ForecastCoverageConfiguration).order_by(
        ForecastCoverageConfiguration.id  # noqa
    )
    if climatic_indicator_filter is not None:
        statement = statement.where(
            ForecastCoverageConfiguration.climatic_indicator_id  # noqa
            == climatic_indicator_filter.id
        )
    if climatic_indicator_name_filter is not None:
        filter_ = climatic_indicator_name_filter.replace("%", "")
        filter_ = f"%{filter_}%"
        statement = statement.join(
            ClimaticIndicator,  # noqa
            ClimaticIndicator.id  # noqa
            == ForecastCoverageConfiguration.climatic_indicator_id,  # noqa
        ).where(ClimaticIndicator.name.ilike(filter_))  # noqa
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_forecast_coverage_configurations(
    session: sqlmodel.Session,
    climatic_indicator_name_filter: Optional[str] = None,
    climatic_indicator_filter: Optional[ClimaticIndicator] = None,
) -> Sequence[ForecastCoverageConfiguration]:
    _, num_total = list_forecast_coverage_configurations(
        session,
        limit=1,
        include_total=True,
        climatic_indicator_name_filter=climatic_indicator_name_filter,
        climatic_indicator_filter=climatic_indicator_filter,
    )
    result, _ = list_forecast_coverage_configurations(
        session,
        limit=num_total,
        include_total=False,
        climatic_indicator_name_filter=climatic_indicator_name_filter,
        climatic_indicator_filter=climatic_indicator_filter,
    )
    return result


def collect_all_forecast_coverage_configurations_with_identifier_filter(
    session: sqlmodel.Session,
    identifier_filter: Optional[str] = None,
) -> list[ForecastCoverageConfiguration]:
    all_fccs = collect_all_forecast_coverage_configurations(session)
    if identifier_filter is not None:
        result = [fcc for fcc in all_fccs if identifier_filter in fcc.identifier]
    else:
        result = all_fccs
    return result


def get_forecast_coverage_configuration(
    session: sqlmodel.Session,
    forecast_coverage_configuration_id: int,
) -> Optional[ForecastCoverageConfiguration]:
    return session.get(
        ForecastCoverageConfiguration, forecast_coverage_configuration_id
    )


def _get_five_part_fcc(
    session: sqlmodel.Session,
    climatic_indicator: ClimaticIndicator,
    spatial_region: SpatialRegion,
) -> Optional[ForecastCoverageConfiguration]:
    statement = sqlmodel.select(ForecastCoverageConfiguration).where(
        ForecastCoverageConfiguration.climatic_indicator_id  # noqa
        == climatic_indicator.id,
        ForecastCoverageConfiguration.spatial_region_id == spatial_region.id,  # noqa
    )
    query_result = session.exec(statement).all()  # noqa
    # choose the item that has more than one forecast model and more than one
    # year period
    result = None
    for fcc in query_result:
        fcc: ForecastCoverageConfiguration
        if len(fcc.forecast_model_links) > 1 and len(fcc.year_periods) > 1:
            result = fcc
            break

    # # choose the shorter identifier of those forecast coverage configurations
    # # found in the DB
    # result = None
    # for fcc in query_result:
    #     fcc: ForecastCoverageConfiguration
    #     if result is None:
    #         result = fcc
    #     else:
    #         result = result if len(result.identifier) < len(fcc.identifier) else fcc
    return result


def _get_six_part_fcc(
    session: sqlmodel.Session,
    climatic_indicator: ClimaticIndicator,
    spatial_region: SpatialRegion,
    sixth_part: str,
) -> Optional[ForecastCoverageConfiguration]:
    """Try to find a forecast coverage identifier made up of six parts.

    The sixth part can either represent a forecast model or a year period. In this
    function we start by checking whether thhe sixth partt is a forecast model and
    then we check if it is a year period.
    """
    statement = sqlmodel.select(ForecastCoverageConfiguration).where(
        ForecastCoverageConfiguration.climatic_indicator_id  # noqa
        == climatic_indicator.id,
        ForecastCoverageConfiguration.spatial_region_id == spatial_region.id,  # noqa
    )
    forecast_model_name = sixth_part
    forecast_model = get_forecast_model_by_name(session, forecast_model_name)
    result = None
    if forecast_model is not None:
        statement = statement.join(
            ForecastCoverageConfigurationForecastModelLink,
            (  # noqa
                ForecastCoverageConfiguration.id  # noqa
                == ForecastCoverageConfigurationForecastModelLink.forecast_coverage_configuration_id  # noqa
            ),
        ).where(
            ForecastCoverageConfigurationForecastModelLink.forecast_model_id  # noqa
            == forecast_model.id
        )
        query_result: Sequence[ForecastCoverageConfiguration] = session.exec(
            statement
        ).all()
        for fcc in query_result:
            if len(fcc.forecast_model_links) == 1 and len(fcc.year_periods) > 1:
                result = fcc
                break
    else:
        year_period_value = sixth_part
        try:
            year_period = ForecastYearPeriod(year_period_value)
        except ValueError:
            raise exceptions.InvalidForecastYearPeriodError(
                f"{year_period_value!r} is not a valid forecast year period"
            )
        else:
            statement = statement.where(
                year_period.name
                == sqlalchemy.any_(ForecastCoverageConfiguration.year_periods)  # noqa
            )
            query_result: Sequence[ForecastCoverageConfiguration] = session.exec(
                statement
            ).all()  # noqa
            for fcc in query_result:
                if len(fcc.year_periods) == 1 and len(fcc.forecast_model_links) > 1:
                    result = fcc
                    break
    return result


def _get_seven_part_fcc(
    session: sqlmodel.Session,
    climatic_indicator: ClimaticIndicator,
    spatial_region: SpatialRegion,
    sixth_part: str,
    seventh_part: str,
) -> Optional[ForecastCoverageConfiguration]:
    """Try to find a forecast coverage identifier made up of seven parts.

    The sixth and seventh parts will be the forecast model and the year period,
    respectively.
    """
    statement = sqlmodel.select(ForecastCoverageConfiguration).where(
        ForecastCoverageConfiguration.climatic_indicator_id  # noqa
        == climatic_indicator.id,  # noqa
        ForecastCoverageConfiguration.spatial_region_id == spatial_region.id,  # noqa
    )
    forecast_model_name = sixth_part
    forecast_model = get_forecast_model_by_name(session, forecast_model_name)
    if forecast_model is None:
        raise exceptions.InvalidForecastCoverageConfigurationIdentifierError(
            f"{forecast_model_name!r} is not a valid forecast model"
        )
    year_period_value = seventh_part
    try:
        year_period = ForecastYearPeriod(year_period_value)
    except ValueError:
        raise exceptions.InvalidForecastYearPeriodError(
            f"{year_period_value!r} is not a valid forecast year period"
        )
    statement = (
        statement.join(
            ForecastCoverageConfigurationForecastModelLink,
            (  # noqa
                ForecastCoverageConfiguration.id  # noqa
                == ForecastCoverageConfigurationForecastModelLink.forecast_coverage_configuration_id  # noqa
            ),
        )
        .where(
            ForecastCoverageConfigurationForecastModelLink.forecast_model_id  # noqa
            == forecast_model.id
        )
        .where(
            year_period.name
            == sqlalchemy.any_(ForecastCoverageConfiguration.year_periods)  # noqa
        )
    )
    query_result: Sequence[ForecastCoverageConfiguration] = session.exec(
        statement
    ).all()
    result = None
    for fcc in query_result:
        if len(fcc.forecast_model_links) == 1 and len(fcc.year_periods) == 1:
            result = fcc
            break
    return result


def get_forecast_coverage_configuration_by_identifier(
    session: sqlmodel.Session, identifier: str
) -> Optional[ForecastCoverageConfiguration]:
    error_message = f"{identifier!r} is not a valid forecast coverage identifier"
    parts = identifier.split("-")
    if parts[0] == DataCategory.FORECAST.value:
        if len(parts) >= 5:
            climatic_indicator_identifier = "-".join(parts[1:4])
            climatic_indicator = get_climatic_indicator_by_identifier(
                session, climatic_indicator_identifier
            )
            if climatic_indicator is None:
                raise exceptions.InvalidClimaticIndicatorIdentifierError(
                    f"{climatic_indicator_identifier!r} is not a valid climatic "
                    f"indicator identifier"
                )
            spatial_region_name = parts[4]
            spatial_region = get_spatial_region_by_name(session, spatial_region_name)
            if spatial_region is None:
                raise exceptions.InvalidSpatialRegionNameError(
                    f"{spatial_region_name!r} is not a valid spatial region name"
                )

            if len(parts) == 5:
                result = _get_five_part_fcc(session, climatic_indicator, spatial_region)
            elif len(parts) == 6:
                result = _get_six_part_fcc(
                    session, climatic_indicator, spatial_region, parts[5]
                )
            elif len(parts) == 7:
                result = _get_seven_part_fcc(
                    session, climatic_indicator, spatial_region, parts[5], parts[6]
                )
            else:
                raise exceptions.InvalidForecastCoverageConfigurationIdentifierError(
                    error_message + " - identifier is too long"
                )
            return result
        else:
            raise exceptions.InvalidForecastCoverageConfigurationIdentifierError(
                error_message + " - identifier is too short"
            )
    else:
        raise exceptions.InvalidForecastCoverageConfigurationIdentifierError(
            error_message
        )


def create_forecast_coverage_configuration(
    session: sqlmodel.Session,
    forecast_coverage_configuration_create: ForecastCoverageConfigurationCreate,
) -> ForecastCoverageConfiguration:
    db_forecast_coverage_configuration = ForecastCoverageConfiguration(
        **forecast_coverage_configuration_create.model_dump(
            exclude={
                "time_windows",
                "observation_series_configurations",
            }
        )
    )
    session.add(db_forecast_coverage_configuration)
    for forecast_model_id in forecast_coverage_configuration_create.forecast_models:
        db_forecast_model = get_forecast_model(session, forecast_model_id)
        if db_forecast_model is not None:
            db_forecast_coverage_configuration.forecast_model_links.append(
                ForecastCoverageConfigurationForecastModelLink(
                    forecast_model_id=forecast_model_id,
                )
            )
        else:
            raise ValueError(f"Forecast model {forecast_model_id!r} not found")
    for forecast_time_window_id in (
        forecast_coverage_configuration_create.forecast_time_windows or []
    ):
        db_forecast_time_window = get_forecast_time_window(
            session, forecast_time_window_id
        )
        if db_forecast_time_window is not None:
            db_forecast_coverage_configuration.forecast_time_window_links.append(
                ForecastCoverageConfigurationForecastTimeWindowLink(
                    forecast_time_window=db_forecast_time_window
                )
            )
        else:
            raise ValueError(
                f"Forecast time window {forecast_time_window_id!r} not found"
            )
    for obs_series_conf_id in (
        forecast_coverage_configuration_create.observation_series_configurations or []
    ):
        db_obs_series_conf = get_observation_series_configuration(
            session, obs_series_conf_id
        )
        if db_obs_series_conf is not None:
            db_forecast_coverage_configuration.observation_series_configuration_links.append(
                ForecastCoverageConfigurationObservationSeriesConfigurationLink(
                    observation_series_configuration=db_obs_series_conf
                )
            )
        else:
            raise ValueError(
                f"observation series configuration {obs_series_conf_id!r} not found"
            )
    session.commit()
    session.refresh(db_forecast_coverage_configuration)
    return db_forecast_coverage_configuration


def update_forecast_coverage_configuration(
    session: sqlmodel.Session,
    db_forecast_coverage_configuration: ForecastCoverageConfiguration,
    forecast_coverage_configuration_update: ForecastCoverageConfigurationUpdate,
) -> ForecastCoverageConfiguration:
    """Update a forecast coverage configuration."""
    existing_forecast_model_links_to_keep = []
    existing_forecast_model_links_discard = []
    for (
        existing_forecast_model_link
    ) in db_forecast_coverage_configuration.forecast_model_links:
        has_been_requested_to_remove = (
            existing_forecast_model_link.forecast_model_id
            not in [
                fm_id
                for fm_id in forecast_coverage_configuration_update.forecast_models
            ]
        )
        if not has_been_requested_to_remove:
            existing_forecast_model_links_to_keep.append(existing_forecast_model_link)
        else:
            existing_forecast_model_links_discard.append(existing_forecast_model_link)
    db_forecast_coverage_configuration.forecast_model_links = (
        existing_forecast_model_links_to_keep
    )
    for to_discard in existing_forecast_model_links_discard:
        session.delete(to_discard)
    existing_time_window_links_to_keep = []
    existing_time_window_links_discard = []
    for (
        existing_time_window_link
    ) in db_forecast_coverage_configuration.forecast_time_window_links:
        has_been_requested_to_remove = (
            existing_time_window_link.forecast_time_window_id
            not in [
                tw_id
                for tw_id in forecast_coverage_configuration_update.forecast_time_windows
            ]
        )
        if not has_been_requested_to_remove:
            existing_time_window_links_to_keep.append(existing_time_window_link)
        else:
            existing_time_window_links_discard.append(existing_time_window_link)
    db_forecast_coverage_configuration.forecast_time_window_links = (
        existing_time_window_links_to_keep
    )
    for to_discard in existing_time_window_links_discard:
        session.delete(to_discard)
    existing_obs_series_conf_links_to_keep = []
    existing_obs_series_conf_links_discard = []
    for (
        existing_obs_series_conf_link
    ) in db_forecast_coverage_configuration.observation_series_configuration_links:
        has_been_requested_to_remove = (
            existing_obs_series_conf_link.observation_series_configuration_id
            not in [
                osc_id
                for osc_id in forecast_coverage_configuration_update.observation_series_configurations
            ]
        )
        if not has_been_requested_to_remove:
            existing_obs_series_conf_links_to_keep.append(existing_obs_series_conf_link)
        else:
            existing_obs_series_conf_links_discard.append(existing_obs_series_conf_link)
    db_forecast_coverage_configuration.observation_series_configuration_links = (
        existing_obs_series_conf_links_to_keep
    )
    for to_discard in existing_obs_series_conf_links_discard:
        session.delete(to_discard)

    for forecast_model_id in forecast_coverage_configuration_update.forecast_models:
        already_there = forecast_model_id in (
            fml.forecast_model_id
            for fml in db_forecast_coverage_configuration.forecast_model_links
        )
        if not already_there:
            db_forecast_model_link = ForecastCoverageConfigurationForecastModelLink(
                forecast_model_id=forecast_model_id,
            )
            db_forecast_coverage_configuration.forecast_model_links.append(
                db_forecast_model_link
            )
    for time_window_id in forecast_coverage_configuration_update.forecast_time_windows:
        already_there = time_window_id in (
            twl.forecast_time_window_id
            for twl in db_forecast_coverage_configuration.forecast_time_window_links
        )
        if not already_there:
            db_time_window_link = ForecastCoverageConfigurationForecastTimeWindowLink(
                forecast_time_window_id=time_window_id
            )
            db_forecast_coverage_configuration.forecast_time_window_links.append(
                db_time_window_link
            )
    for (
        obs_series_conf_id
    ) in forecast_coverage_configuration_update.observation_series_configurations:
        already_there = obs_series_conf_id in (
            oscl.observation_series_configuration_id
            for oscl in db_forecast_coverage_configuration.observation_series_configuration_links
        )
        if not already_there:
            db_obs_series_conf_link = (
                ForecastCoverageConfigurationObservationSeriesConfigurationLink(
                    observation_series_configuration_id=obs_series_conf_id
                )
            )
            db_forecast_coverage_configuration.observation_series_configuration_links.append(
                db_obs_series_conf_link
            )
    data_ = forecast_coverage_configuration_update.model_dump(
        exclude={
            "time_windows",
            "observation_series_configurations",
        },
        exclude_unset=True,
        exclude_none=True,
    )
    for key, value in data_.items():
        setattr(db_forecast_coverage_configuration, key, value)
    session.add(db_forecast_coverage_configuration)
    session.commit()
    session.refresh(db_forecast_coverage_configuration)
    return db_forecast_coverage_configuration


def delete_forecast_coverage_configuration(
    session: sqlmodel.Session, forecast_coverage_configuration_id: int
) -> None:
    db_item = get_forecast_coverage_configuration(
        session, forecast_coverage_configuration_id
    )
    if db_item is not None:
        session.delete(db_item)
        session.commit()
    else:
        raise RuntimeError("Forecast coverage configuration not found")


def list_forecast_models(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    name_filter: str | None = None,
    include_total: bool = False,
) -> tuple[Sequence[ForecastModel], Optional[int]]:
    """List existing forecast models."""
    statement = sqlmodel.select(ForecastModel).order_by(
        ForecastModel.sort_order  # noqa
    )
    if name_filter is not None:
        statement = add_substring_filter(
            statement,
            name_filter,
            ForecastModel.internal_value,  # noqa
        )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_forecast_models(
    session: sqlmodel.Session,
    name_filter: str | None = None,
) -> Sequence[ForecastModel]:
    _, num_total = list_forecast_models(
        session,
        limit=1,
        name_filter=name_filter,
        include_total=True,
    )
    result, _ = list_forecast_models(
        session,
        limit=num_total,
        name_filter=name_filter,
        include_total=False,
    )
    return result


def get_forecast_model(
    session: sqlmodel.Session,
    forecast_model_id: int,
) -> Optional[ForecastModel]:
    return session.get(ForecastModel, forecast_model_id)


def get_forecast_model_by_name(
    session: sqlmodel.Session, name: str
) -> Optional[ForecastModel]:
    """Get a forecast model by its name."""
    return session.exec(
        sqlmodel.select(ForecastModel).where(  # noqa
            ForecastModel.name == name  # noqa
        )
    ).first()


def create_forecast_model(
    session: sqlmodel.Session,
    forecast_model_create: ForecastModelCreate,
) -> ForecastModel:
    """Create a new forecast model."""
    db_forecast_model = ForecastModel(
        **forecast_model_create.model_dump(),
    )
    session.add(db_forecast_model)
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        session.refresh(db_forecast_model)
    return db_forecast_model


def update_forecast_model(
    session: sqlmodel.Session,
    db_forecast_model: ForecastModel,
    forecast_model_update: ForecastModelUpdate,
) -> ForecastModel:
    """Update a forecast model."""
    for key, value in forecast_model_update.model_dump().items():
        setattr(db_forecast_model, key, value)
    session.add(db_forecast_model)
    session.commit()
    session.refresh(db_forecast_model)
    return db_forecast_model


def delete_forecast_model(session: sqlmodel.Session, forecast_model_id: int) -> None:
    db_item = get_forecast_model(session, forecast_model_id)
    if db_item is not None:
        session.delete(db_item)
        session.commit()
    else:
        raise RuntimeError("Forecast model not found")


def list_forecast_time_windows(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    name_filter: str | None = None,
    include_total: bool = False,
) -> tuple[Sequence[ForecastTimeWindow], Optional[int]]:
    """List existing forecast time windows."""
    statement = sqlmodel.select(ForecastTimeWindow).order_by(
        ForecastTimeWindow.sort_order  # noqa
    )
    if name_filter is not None:
        statement = add_substring_filter(
            statement,
            name_filter,
            ForecastModel.internal_value,  # noqa
        )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_forecast_time_windows(
    session: sqlmodel.Session,
    name_filter: str | None = None,
) -> Sequence[ForecastTimeWindow]:
    _, num_total = list_forecast_time_windows(
        session,
        limit=1,
        name_filter=name_filter,
        include_total=True,
    )
    result, _ = list_forecast_time_windows(
        session,
        limit=num_total,
        name_filter=name_filter,
        include_total=False,
    )
    return result


def get_forecast_time_window(
    session: sqlmodel.Session,
    forecast_time_window_id: int,
) -> Optional[ForecastTimeWindow]:
    return session.get(ForecastTimeWindow, forecast_time_window_id)


def get_forecast_time_window_by_name(
    session: sqlmodel.Session, name: str
) -> Optional[ForecastTimeWindow]:
    """Get a forecast time window by its name."""
    return session.exec(
        sqlmodel.select(ForecastTimeWindow).where(  # noqa
            ForecastTimeWindow.name == name  # noqa
        )
    ).first()


def create_forecast_time_window(
    session: sqlmodel.Session,
    forecast_time_window_create: ForecastTimeWindowCreate,
) -> ForecastTimeWindow:
    """Create a new forecast time window."""
    db_tw = ForecastTimeWindow(
        **forecast_time_window_create.model_dump(),
    )
    session.add(db_tw)
    try:
        session.commit()
    except sqlalchemy.exc.DBAPIError:
        raise
    else:
        session.refresh(db_tw)
        return db_tw


def update_forecast_time_window(
    session: sqlmodel.Session,
    db_forecast_time_window: ForecastTimeWindow,
    forecast_time_window_update: ForecastTimeWindowUpdate,
) -> ForecastTimeWindow:
    """Update an forecast time window."""
    for key, value in forecast_time_window_update.model_dump().items():
        setattr(db_forecast_time_window, key, value)
    session.add(db_forecast_time_window)
    session.commit()
    session.refresh(db_forecast_time_window)
    return db_forecast_time_window


def delete_forecast_time_window(
    session: sqlmodel.Session, forecast_time_window_id: int
) -> None:
    db_item = get_forecast_time_window(session, forecast_time_window_id)
    if db_item is not None:
        session.delete(db_item)
        session.commit()
    else:
        raise RuntimeError("Forecast time window not found")


def generate_forecast_coverages_from_configuration(
    forecast_coverage_configuration: ForecastCoverageConfiguration,
) -> list[ForecastCoverageInternal]:
    result = []
    to_combine = [
        forecast_coverage_configuration.scenarios,
        forecast_coverage_configuration.year_periods,
        forecast_coverage_configuration.forecast_model_links,
    ]
    has_time_window = (
        len(forecast_coverage_configuration.forecast_time_window_links) > 0
    )
    if has_time_window:
        to_combine.append(forecast_coverage_configuration.forecast_time_window_links)
    for combination in itertools.product(*to_combine):
        scenario, year_period, fm_link = combination[:3]
        tw_link = None
        if has_time_window:
            tw_link = combination[3]
        try:
            result.append(
                ForecastCoverageInternal(
                    configuration=forecast_coverage_configuration,
                    scenario=scenario,
                    forecast_model=fm_link.forecast_model,
                    forecast_year_period=year_period,
                    forecast_time_window=tw_link.forecast_time_window
                    if tw_link
                    else None,
                )
            )
        except (
            exceptions.InvalidForecastModelError,
            exceptions.InvalidForecastTimeWindowError,
        ):
            logger.exception(
                f"Could not generate forecast coverage from combination {combination}"
            )
    return result


def generate_forecast_coverages_for_other_models(
    session: sqlmodel.Session,
    forecast_coverage: ForecastCoverageInternal,
) -> list[ForecastCoverageInternal]:
    """Get a list of forecast coverages with the other forecast models.

    The implementation of this function is a bit complex because it is possible
    that forecast models for the same climatic indicator are distributed across
    multiple forecast coverage configurations.
    """

    all_forecast_models = collect_all_forecast_models(session)
    other_model_ids = [
        fm.id
        for fm in all_forecast_models
        if fm.id != forecast_coverage.forecast_model.id
    ]

    indicator = forecast_coverage.configuration.climatic_indicator
    conf_ids = set()
    for candidate_forecast_cov_conf in indicator.forecast_coverage_configurations:
        for candidate_model_link in candidate_forecast_cov_conf.forecast_model_links:
            if candidate_model_link.forecast_model_id in other_model_ids:
                # the respective forecast_cov_conf is able to generate forecast
                # coverages with this forecast model
                conf_ids.add(candidate_forecast_cov_conf.id)
    candidate_forecast_coverages = []
    for conf_id in conf_ids:
        forecast_cov_conf = get_forecast_coverage_configuration(session, conf_id)
        possible_forecast_coverages = generate_forecast_coverages_from_configuration(
            forecast_cov_conf
        )
        candidate_forecast_coverages.extend(possible_forecast_coverages)

    result = []
    for candidate in candidate_forecast_coverages:
        same_scenario = candidate.scenario == forecast_coverage.scenario
        same_year_period = (
            candidate.forecast_year_period == forecast_coverage.forecast_year_period
        )
        different_model = (
            candidate.forecast_model.id != forecast_coverage.forecast_model.id
        )
        model_already_in_result = candidate.forecast_model.id in [
            f.forecast_model.id for f in result
        ]
        if same_scenario and same_year_period and different_model:
            if not model_already_in_result:
                logger.debug(f"Adding {candidate.identifier!r} to the result...")
                result.append(candidate)
            else:
                logger.debug(
                    f"Not Adding {candidate.identifier!r} to the result because "
                    f"another forecast coverage with the same forecast model is "
                    f"already present in the result..."
                )
    return result


def get_forecast_coverage_data_series(session: sqlmodel.Session, identifier: str):
    # a forecast data series is always identified by a string like:
    # {forecast_coverage_identifier}-{series_identifier}, where {series_identifier} is:
    # {dataset_type}-{wkt_location}-{temporal_range_start}-{temporal_range_end}-{smoothing_identifier}
    all_parts = identifier.split("-")
    forecast_coverage_identifier = "-".join(all_parts[:-5])
    forecast_coverage = get_forecast_coverage(session, forecast_coverage_identifier)
    if forecast_coverage is None:
        raise exceptions.InvalidForecastCoverageDataSeriesIdentifierError(
            f"forecast coverage {forecast_coverage_identifier!r} does not exist"
        )
    raw_ds_type, raw_location, raw_start, raw_end, raw_processing_method = identifier
    try:
        dataset_type = DatasetType(raw_ds_type)
    except ValueError:
        raise exceptions.InvalidForecastCoverageDataSeriesIdentifierError(
            f"dataset type {raw_ds_type} does not exist"
        )
    try:
        location = shapely.Point(geohashr.decode(raw_location))
    except ValueError:
        raise exceptions.InvalidForecastCoverageDataSeriesIdentifierError(
            f"location {raw_location} is invalid"
        )
    try:
        start = (
            dt.date(int(raw_start[:4]), int(raw_start[4:6]), int(raw_start[6:8]))
            if raw_start != "*"
            else None
        )
    except IndexError:
        raise exceptions.InvalidForecastCoverageDataSeriesIdentifierError(
            f"temporal range start {raw_start!r} is invalid"
        )
    try:
        end = (
            dt.date(int(raw_end[:4]), int(raw_end[4:6]), int(raw_end[6:8]))
            if raw_end != "*"
            else None
        )
    except IndexError:
        raise exceptions.InvalidForecastCoverageDataSeriesIdentifierError(
            f"temporal range start {raw_start!r} is invalid"
        )
    try:
        processing_method = CoverageTimeSeriesProcessingMethod(raw_processing_method)
    except ValueError:
        raise exceptions.InvalidForecastCoverageDataSeriesIdentifierError(
            f"Processing method {raw_processing_method} does not exist"
        )
    return ForecastDataSeries(
        forecast_coverage=forecast_coverage,
        dataset_type=dataset_type,
        processing_method=processing_method,
        temporal_start=start,
        temporal_end=end,
        location=location,
    )


def get_forecast_coverage(
    session: sqlmodel.Session, identifier: str
) -> Optional[ForecastCoverageInternal]:
    parts = identifier.split("-")
    time_window_name = None
    # first try to find the forecast coverage configuration using the longest
    # possible identifier, which is with seven parts...
    possible_seven_part_cov_conf_identifier = "-".join(parts[:7])
    try:
        forecast_cov_conf = get_forecast_coverage_configuration_by_identifier(
            session, possible_seven_part_cov_conf_identifier
        )
    except exceptions.ArpavError:
        forecast_cov_conf = None
    if forecast_cov_conf is not None:
        forecast_model_name = forecast_cov_conf.forecast_model_links[
            0
        ].forecast_model.name
        year_period_value = forecast_cov_conf.year_periods[0].value
        remaining_parts = parts[7:]
        scenario_value = remaining_parts[0]
        if len(remaining_parts) > 1:
            time_window_name = remaining_parts[1]
    else:
        # ... if it can't be found, then try a shorter forecast coverage
        # configuration identifier, using six parts
        possible_six_part_cov_conf_identifier = "-".join(parts[:6])
        try:
            forecast_cov_conf = get_forecast_coverage_configuration_by_identifier(
                session, possible_six_part_cov_conf_identifier
            )
        except exceptions.ArpavError:
            forecast_cov_conf = None
        if forecast_cov_conf is not None:
            remaining_parts = parts[6:]
            forecast_model_or_scenario_value, scenario_or_year_period = remaining_parts[
                :2
            ]
            if len(forecast_cov_conf.forecast_model_links) == 1:
                forecast_model_name = forecast_cov_conf.forecast_model_links[
                    0
                ].forecast_model.name
                scenario_value = forecast_model_or_scenario_value
                year_period_value = scenario_or_year_period
            elif len(forecast_cov_conf.year_periods) == 1:
                year_period_value = forecast_cov_conf.year_periods[0].value
                forecast_model_name = forecast_model_or_scenario_value
                scenario_value = scenario_or_year_period
            else:
                raise RuntimeError(
                    f"Something went wrong with the detection of this forecast "
                    f"coverage identifier: {identifier!r}"
                )
            if len(remaining_parts) > 2:
                time_window_name = remaining_parts[2]
        else:
            # ... if it still can't be found, then try the shortest possible forecast
            # coverage configuration identifier, using five parts
            possible_five_part_cov_conf_identifier = "-".join(parts[:5])
            forecast_cov_conf = get_forecast_coverage_configuration_by_identifier(
                session, possible_five_part_cov_conf_identifier
            )
            if forecast_cov_conf is not None:
                remaining_parts = parts[5:]
                (
                    forecast_model_name,
                    scenario_value,
                    year_period_value,
                ) = remaining_parts[:3]
                if len(remaining_parts) > 3:
                    time_window_name = remaining_parts[3]
            else:
                raise exceptions.InvalidForecastCoverageIdentifierError(
                    f"Could not find the forecast coverage's respective configuration "
                    f"- Tried: {possible_seven_part_cov_conf_identifier!r}, "
                    f"{possible_six_part_cov_conf_identifier!r} and "
                    f"{possible_five_part_cov_conf_identifier!r}"
                )
    return ForecastCoverageInternal(
        configuration=forecast_cov_conf,
        scenario=ForecastScenario(scenario_value),
        forecast_model=get_forecast_model_by_name(session, forecast_model_name),
        forecast_year_period=ForecastYearPeriod(year_period_value),
        forecast_time_window=(
            get_forecast_time_window_by_name(session, time_window_name)
            if time_window_name is not None
            else None
        ),
    )


def legacy_list_forecast_coverage_configurations(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    name_filter: Optional[str] = None,
    conf_param_filter: Optional[LegacyConfParamFilterValues],
):
    """List forecast coverage configurations.

    NOTE:

    This function supports a bunch of search filters that were previously provided by
    the more generic `configuration_parameter` instances, which were available in
    an early version of the project. This is kept only for compatibility reasons -
    newer code should use `list_forecast_coverage_configurations()` instead.
    """
    statement = (
        sqlmodel.select(ForecastCoverageConfiguration)
        .join(
            ClimaticIndicator,
            ClimaticIndicator.id == ForecastCoverageConfiguration.climatic_indicator_id,  # noqa
        )
        .order_by(ClimaticIndicator.sort_order)  # noqa
    )
    if name_filter is not None:
        statement = add_substring_filter(
            statement,
            name_filter,
            ClimaticIndicator.name,  # noqa
        )
    if conf_param_filter is not None:
        if conf_param_filter.climatic_indicator is not None:
            statement = statement.where(
                ClimaticIndicator.id  # noqa
                == conf_param_filter.climatic_indicator.id
            )
        else:
            if conf_param_filter.climatological_variable is not None:
                statement = statement.where(
                    ClimaticIndicator.name  # noqa
                    == conf_param_filter.climatological_variable
                )
            if conf_param_filter.measure is not None:
                statement = statement.where(
                    ClimaticIndicator.measure_type  # noqa
                    == conf_param_filter.measure.name
                )
            if conf_param_filter.aggregation_period is not None:
                statement = statement.where(
                    ClimaticIndicator.aggregation_period  # noqa
                    == conf_param_filter.aggregation_period.name
                )
        if conf_param_filter.climatological_model is not None:
            statement = (
                statement.join(
                    ForecastCoverageConfigurationForecastModelLink,
                    ForecastCoverageConfiguration.id  # noqa
                    == ForecastCoverageConfigurationForecastModelLink.forecast_coverage_configuration_id,  # noqa
                )
                .join(
                    ForecastModel,
                    ForecastModel.id  # noqa
                    == ForecastCoverageConfigurationForecastModelLink.forecast_model_id,  # noqa
                )
                .where(
                    ForecastModel.id  # noqa
                    == conf_param_filter.climatological_model.id
                )
            )
        if conf_param_filter.scenario is not None:
            statement = statement.where(
                conf_param_filter.scenario.name
                == sqlalchemy.any_(ForecastCoverageConfiguration.scenarios)  # noqa
            )
        if conf_param_filter.time_window is not None:
            statement = (
                statement.join(
                    ForecastCoverageConfigurationForecastTimeWindowLink,
                    ForecastCoverageConfiguration.id  # noqa
                    == ForecastCoverageConfigurationForecastTimeWindowLink.forecast_coverage_configuration_id,  # noqa
                )
                .join(
                    ForecastTimeWindow,
                    ForecastTimeWindow.id  # noqa
                    == ForecastCoverageConfigurationForecastTimeWindowLink.forecast_time_window_id,  # noqa
                )
                .where(
                    ForecastTimeWindow.id == conf_param_filter.time_window.id  # noqa
                )
            )
        if conf_param_filter.year_period is not None:
            statement = statement.where(
                conf_param_filter.year_period.name
                == sqlalchemy.any_(ForecastCoverageConfiguration.year_periods)  # noqa
            )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def legacy_collect_all_forecast_coverage_configurations(
    session: sqlmodel.Session,
    *,
    name_filter: Optional[str] = None,
    conf_param_filter: Optional[LegacyConfParamFilterValues] = None,
) -> Sequence[ForecastCoverageConfiguration]:
    """Collect all forecast coverage configurations.

    NOTE:

    This function supports a bunch of search filters that were previously provided by
    the more generic `configuration_parameter` instances, which were available in
    an early version of the project. This is kept only for compatibility reasons -
    newer code should use `collect_all_forecast_coverage_configurations()` instead.
    """
    _, num_total = legacy_list_forecast_coverage_configurations(
        session,
        limit=1,
        include_total=True,
        name_filter=name_filter,
        conf_param_filter=conf_param_filter,
    )
    result, _ = legacy_list_forecast_coverage_configurations(
        session,
        limit=num_total,
        include_total=False,
        name_filter=name_filter,
        conf_param_filter=conf_param_filter,
    )
    return result


def legacy_list_forecast_coverages(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    name_filter: list[str] | None = None,
    conf_param_filter: Optional[LegacyConfParamFilterValues] = None,
) -> tuple[list[ForecastCoverageInternal], Optional[int]]:
    all_cov_confs = legacy_collect_all_forecast_coverage_configurations(
        session, conf_param_filter=conf_param_filter
    )
    result = []
    for cov_conf in all_cov_confs:
        result.extend(generate_forecast_coverages_from_configuration(cov_conf))
    if name_filter is not None:
        for fragment in name_filter:
            result = [fc for fc in result if fragment in fc.identifier]
    return result[offset : offset + limit], len(result) if include_total else None
