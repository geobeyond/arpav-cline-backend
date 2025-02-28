import itertools
import logging
from typing import (
    Optional,
    Sequence,
    Union,
)

import sqlalchemy
import sqlmodel

from ..schemas.base import SpatialRegion
from ..schemas.climaticindicators import (
    ClimaticIndicator,
)
from ..schemas.coverages import (
    HistoricalCoverageInternal,
    HistoricalCoverageConfiguration,
    HistoricalCoverageConfigurationCreate,
    HistoricalCoverageConfigurationObservationSeriesConfigurationLink,
    HistoricalCoverageConfigurationUpdate,
    HistoricalYearPeriodGroup,
    HistoricalYearPeriodGroupCreate,
    HistoricalYearPeriodGroupUpdate,
    LegacyConfParamFilterValues,
)
from ..schemas.static import (
    AggregationPeriod,
    DataCategory,
    HistoricalReferencePeriod,
    HistoricalYearPeriod,
    HistoricalDecade,
    MeasureType,
)
from .base import (
    add_multiple_values_filter,
    add_values_in_list_filter,
    add_substring_filter,
    get_total_num_records,
)
from .climaticindicators import (
    collect_all_climatic_indicators,
    get_climatic_indicator_by_identifier,
)
from .observationseries import get_observation_series_configuration
from .spatialregions import get_spatial_region_by_name

logger = logging.getLogger(__name__)


def list_historical_coverage_configurations(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    climatic_indicator_name_filter: Optional[str] = None,
    climatic_indicator_filter: Optional[ClimaticIndicator] = None,
    year_period_filter: Optional[
        Union[list[HistoricalYearPeriod], HistoricalYearPeriod]
    ] = None,
    reference_period_filter: Optional[
        Union[list[HistoricalReferencePeriod], HistoricalReferencePeriod]
    ] = None,
    decade_filter: Optional[Union[list[HistoricalDecade], HistoricalDecade]] = None,
) -> tuple[Sequence[HistoricalCoverageConfiguration], Optional[int]]:
    """List existing historical coverage configurations."""
    statement = sqlmodel.select(HistoricalCoverageConfiguration).order_by(
        HistoricalCoverageConfiguration.id
    )
    if climatic_indicator_filter is not None:
        statement = statement.where(
            HistoricalCoverageConfiguration.climatic_indicator_id
            == climatic_indicator_filter.id
        )
    if climatic_indicator_name_filter is not None:
        filter_ = climatic_indicator_name_filter.replace("%", "")
        filter_ = f"%{filter_}%"
        statement = statement.join(
            ClimaticIndicator,
            ClimaticIndicator.id
            == HistoricalCoverageConfiguration.climatic_indicator_id,
        ).where(ClimaticIndicator.name.ilike(filter_))
    if reference_period_filter is not None:
        if not isinstance(reference_period_filter, list):
            reference_periods = [reference_period_filter.name]
        else:
            reference_periods = [rp.name for rp in reference_period_filter]
        if len(reference_periods) == 1:
            statement = statement.where(
                HistoricalCoverageConfiguration.reference_period == reference_periods[0]
            )
        else:
            statement = statement.where(
                HistoricalCoverageConfiguration.reference_period.in_(reference_periods)
            )
    if year_period_filter is not None:
        statement = statement.join(
            HistoricalYearPeriodGroup,
            HistoricalCoverageConfiguration.year_period_group_id
            == HistoricalYearPeriodGroup.id,
        )
        statement = add_values_in_list_filter(
            statement, year_period_filter, HistoricalYearPeriodGroup.year_periods
        )
    if decade_filter is not None:
        if not isinstance(decade_filter, list):
            decades = [decade_filter.name]
        else:
            decades = [d.name for d in decade_filter]
        if len(decades) == 1:
            statement = statement.where(
                decades[0] == sqlalchemy.any_(HistoricalCoverageConfiguration.decades)
            )
        else:
            statement = statement.where(
                sqlalchemy.or_(
                    *[
                        d == sqlalchemy.any_(HistoricalCoverageConfiguration.decades)
                        for d in decades
                    ]
                )
            )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_historical_coverage_configurations(
    session: sqlmodel.Session,
    climatic_indicator_name_filter: Optional[str] = None,
    climatic_indicator_filter: Optional[ClimaticIndicator] = None,
    year_period_filter: Optional[
        Union[list[HistoricalYearPeriod], HistoricalYearPeriod]
    ] = None,
    reference_period_filter: Optional[
        Union[list[HistoricalReferencePeriod], HistoricalReferencePeriod]
    ] = None,
    decade_filter: Optional[Union[list[HistoricalDecade], HistoricalDecade]] = None,
) -> Sequence[HistoricalCoverageConfiguration]:
    _, num_total = list_historical_coverage_configurations(
        session,
        limit=1,
        include_total=True,
        climatic_indicator_name_filter=climatic_indicator_name_filter,
        climatic_indicator_filter=climatic_indicator_filter,
        year_period_filter=year_period_filter,
        reference_period_filter=reference_period_filter,
        decade_filter=decade_filter,
    )
    result, _ = list_historical_coverage_configurations(
        session,
        limit=num_total,
        include_total=False,
        climatic_indicator_name_filter=climatic_indicator_name_filter,
        climatic_indicator_filter=climatic_indicator_filter,
        year_period_filter=year_period_filter,
        reference_period_filter=reference_period_filter,
        decade_filter=decade_filter,
    )
    return result


def collect_all_historical_coverage_configurations_with_identifier_filter(
    session: sqlmodel.Session,
    identifier_filter: Optional[str] = None,
) -> list[HistoricalCoverageConfiguration]:
    all_hccs = collect_all_historical_coverage_configurations(session)
    if identifier_filter is not None:
        result = [hcc for hcc in all_hccs if identifier_filter in hcc.identifier]
    else:
        result = all_hccs
    return result


def get_historical_coverage_configuration(
    session: sqlmodel.Session,
    historical_coverage_configuration_id: int,
) -> Optional[HistoricalCoverageConfiguration]:
    return session.get(
        HistoricalCoverageConfiguration, historical_coverage_configuration_id
    )


def get_historical_coverage_configuration_by_identifier(
    session: sqlmodel.Session, identifier: str
) -> Optional[HistoricalCoverageConfiguration]:
    parts = identifier.split("-")
    result = None
    if len(parts) in (6, 7) and parts[0] == DataCategory.HISTORICAL.value:
        climatic_indicator_identifier = "-".join(parts[1:4])
        climatic_indicator = get_climatic_indicator_by_identifier(
            session, climatic_indicator_identifier
        )
        if climatic_indicator is not None:
            spatial_region_name = parts[4]
            spatial_region = get_spatial_region_by_name(session, spatial_region_name)
            if spatial_region is not None:
                year_period_group_name = parts[5]
                year_period_group = get_historical_year_period_group_by_name(
                    session, year_period_group_name
                )
                if year_period_group is not None:
                    if len(parts) == 6:
                        result = _get_six_part_hcc(
                            session,
                            climatic_indicator,
                            spatial_region,
                            year_period_group,
                        )
                    else:
                        try:
                            reference_period = HistoricalReferencePeriod(parts[6])
                        except ValueError:
                            pass
                        else:
                            result = _get_seven_part_hcc(
                                session,
                                climatic_indicator,
                                spatial_region,
                                year_period_group,
                                reference_period,
                            )
    else:
        logger.info("Invalid coverage identifier")
    return result


def _get_six_part_hcc(
    session: sqlmodel.Session,
    climatic_indicator: ClimaticIndicator,
    spatial_region: SpatialRegion,
    year_period_group: HistoricalYearPeriodGroup,
) -> Optional[HistoricalCoverageConfiguration]:
    statement = sqlmodel.select(HistoricalCoverageConfiguration).where(
        HistoricalCoverageConfiguration.climatic_indicator_id == climatic_indicator.id,
        HistoricalCoverageConfiguration.spatial_region_id == spatial_region.id,
        HistoricalCoverageConfiguration.year_period_group_id == year_period_group.id,
    )
    query_result = session.exec(statement).all()
    result = None
    for hcc in query_result:
        if len(hcc.identifier.split("-")) == 6:
            result = hcc
            break
    return result


def _get_seven_part_hcc(
    session: sqlmodel.Session,
    climatic_indicator: ClimaticIndicator,
    spatial_region: SpatialRegion,
    year_period_group: HistoricalYearPeriodGroup,
    reference_period: HistoricalReferencePeriod,
) -> Optional[HistoricalCoverageConfiguration]:
    statement = sqlmodel.select(HistoricalCoverageConfiguration).where(
        HistoricalCoverageConfiguration.climatic_indicator_id == climatic_indicator.id,
        HistoricalCoverageConfiguration.spatial_region_id == spatial_region.id,
        HistoricalCoverageConfiguration.year_period_group_id == year_period_group.id,
        reference_period.name == HistoricalCoverageConfiguration.reference_period,
    )
    return session.exec(statement).first()


def create_historical_coverage_configuration(
    session: sqlmodel.Session,
    coverage_configuration_create: HistoricalCoverageConfigurationCreate,
) -> HistoricalCoverageConfiguration:
    db_coverage_configuration = HistoricalCoverageConfiguration(
        **coverage_configuration_create.model_dump(exclude={"year_period_group"}),
        year_period_group_id=coverage_configuration_create.year_period_group,
    )
    session.add(db_coverage_configuration)
    for obs_series_conf_id in (
        coverage_configuration_create.observation_series_configurations or []
    ):
        db_obs_series_conf = get_observation_series_configuration(
            session, obs_series_conf_id
        )
        if db_obs_series_conf is not None:
            db_coverage_configuration.observation_series_configuration_links.append(
                HistoricalCoverageConfigurationObservationSeriesConfigurationLink(
                    observation_series_configuration=db_obs_series_conf
                )
            )
        else:
            raise ValueError(
                f"observation series configuration {obs_series_conf_id!r} not found"
            )
    session.commit()
    session.refresh(db_coverage_configuration)
    return db_coverage_configuration


def update_historical_coverage_configuration(
    session: sqlmodel.Session,
    db_coverage_configuration: HistoricalCoverageConfiguration,
    coverage_configuration_update: HistoricalCoverageConfigurationUpdate,
) -> HistoricalCoverageConfiguration:
    """Update a historical coverage configuration."""
    existing_obs_series_conf_links_to_keep = []
    existing_obs_series_conf_links_discard = []
    for (
        existing_obs_series_conf_link
    ) in db_coverage_configuration.observation_series_configuration_links:
        has_been_requested_to_remove = (
            existing_obs_series_conf_link.observation_series_configuration_id
            not in [
                osc_id
                for osc_id in coverage_configuration_update.observation_series_configurations
            ]
        )
        if not has_been_requested_to_remove:
            existing_obs_series_conf_links_to_keep.append(existing_obs_series_conf_link)
        else:
            existing_obs_series_conf_links_discard.append(existing_obs_series_conf_link)
    db_coverage_configuration.observation_series_configuration_links = (
        existing_obs_series_conf_links_to_keep
    )
    for to_discard in existing_obs_series_conf_links_discard:
        session.delete(to_discard)
    for (
        obs_series_conf_id
    ) in coverage_configuration_update.observation_series_configurations:
        already_there = obs_series_conf_id in (
            oscl.observation_series_configuration_id
            for oscl in db_coverage_configuration.observation_series_configuration_links
        )
        if not already_there:
            db_obs_series_conf_link = (
                HistoricalCoverageConfigurationObservationSeriesConfigurationLink(
                    observation_series_configuration_id=obs_series_conf_id
                )
            )
            db_coverage_configuration.observation_series_configuration_links.append(
                db_obs_series_conf_link
            )
    data_ = coverage_configuration_update.model_dump(
        exclude={"year_period_group"},
        exclude_unset=True,
        exclude_none=True,
    )
    if (
        year_period_group_id := coverage_configuration_update.year_period_group
    ) is not None:
        data_["year_period_group_id"] = year_period_group_id
    for key, value in data_.items():
        setattr(db_coverage_configuration, key, value)
    session.add(db_coverage_configuration)
    session.commit()
    session.refresh(db_coverage_configuration)
    return db_coverage_configuration


def delete_historical_coverage_configuration(
    session: sqlmodel.Session, historical_coverage_configuration_id: int
) -> None:
    db_item = get_historical_coverage_configuration(
        session, historical_coverage_configuration_id
    )
    if db_item is not None:
        session.delete(db_item)
        session.commit()
    else:
        raise RuntimeError("Historical coverage configuration not found")


def generate_historical_coverages_from_configuration(
    historical_coverage_configuration: HistoricalCoverageConfiguration,
) -> list[HistoricalCoverageInternal]:
    result = []
    to_combine = [
        historical_coverage_configuration.year_period_group.year_periods,
    ]
    has_decades = len(historical_coverage_configuration.decades or []) > 0
    if has_decades:
        to_combine.append(historical_coverage_configuration.decades)

    for combination in itertools.product(*to_combine):
        year_period = combination[0]
        decade = combination[1] if has_decades else None
        result.append(
            HistoricalCoverageInternal(
                configuration=historical_coverage_configuration,
                year_period=year_period,
                decade=decade,
            )
        )
    return result


def legacy_collect_all_historical_coverage_configurations(
    session: sqlmodel.Session,
    *,
    name_filter: Optional[str] = None,
    conf_param_filter: Optional[LegacyConfParamFilterValues] = None,
) -> Sequence[HistoricalCoverageConfiguration]:
    """Collect all historical coverage configurations.

    NOTE:

    This function supports a bunch of search filters that were previously provided by
    the more generic `configuration_parameter` instances, which were available in
    an early version of the project. This is kept only for compatibility reasons -
    newer code should use `collect_all_historical_coverage_configurations()` instead.
    """
    _, num_total = legacy_list_historical_coverage_configurations(
        session,
        limit=1,
        include_total=True,
        name_filter=name_filter,
        conf_param_filter=conf_param_filter,
    )
    result, _ = legacy_list_historical_coverage_configurations(
        session,
        limit=num_total,
        include_total=False,
        name_filter=name_filter,
        conf_param_filter=conf_param_filter,
    )
    return result


def legacy_list_historical_coverage_configurations(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    name_filter: Optional[str] = None,
    conf_param_filter: Optional[LegacyConfParamFilterValues],
):
    """List historical coverage configurations.

    NOTE:

    This function supports a bunch of search filters that were previously provided by
    the more generic `configuration_parameter` instances, which were available in
    an early version of the project. This is kept only for compatibility reasons -
    newer code should use `list_historical_coverage_configurations()` instead.
    """
    statement = (
        sqlmodel.select(HistoricalCoverageConfiguration)
        .join(
            ClimaticIndicator,
            ClimaticIndicator.id
            == HistoricalCoverageConfiguration.climatic_indicator_id,  # noqa
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
            if conf_param_filter.historical_variable is not None:
                statement = statement.where(
                    ClimaticIndicator.name  # noqa
                    == conf_param_filter.historical_variable
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
        if conf_param_filter.historical_reference_period is not None:
            statement = statement.where(
                conf_param_filter.historical_reference_period.name
                == HistoricalCoverageConfiguration.reference_period  # noqa
            )
        if conf_param_filter.historical_decade is not None:
            statement = statement.where(
                conf_param_filter.historical_decade.name
                == sqlalchemy.any_(HistoricalCoverageConfiguration.decades)  # noqa
            )
        if conf_param_filter.historical_year_period is not None:
            statement = statement.join(
                HistoricalYearPeriodGroup,
                HistoricalYearPeriodGroup.id
                == HistoricalCoverageConfiguration.year_period_group_id,
            ).where(
                conf_param_filter.historical_year_period.name
                == sqlalchemy.any_(HistoricalYearPeriodGroup.year_periods)
            )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def get_historical_coverage(
    session: sqlmodel.Session, identifier: str
) -> Optional[HistoricalCoverageInternal]:
    parts = identifier.split("-")
    decade = None
    year_period = None
    # historical cov conf has either 6 or 7 parts, then we have the year period and maybe a decade
    # so we can have
    # - 6 + 1 = 7
    # - 6 + 1 + 1 = 8
    # - 7 + 1 = 8
    # - 7 + 1 + 1 = 9
    result = None
    if len(parts) >= 7 and parts[0] == DataCategory.HISTORICAL.value:
        possible_seven_part_historical_cov_conf_identifier = "-".join(parts[:7])
        cov_conf = get_historical_coverage_configuration_by_identifier(
            session, possible_seven_part_historical_cov_conf_identifier
        )
        if cov_conf is not None:
            year_period_value = parts[8]
            try:
                year_period = HistoricalYearPeriod(year_period_value)
            except ValueError:
                pass
            else:
                if len(parts) > 9:
                    decade_value = parts[9]
                    try:
                        decade = HistoricalDecade(decade_value)
                    except ValueError:
                        pass
        else:
            possible_six_part_historical_cov_conf_identifier = "-".join(parts[:6])
            cov_conf = get_historical_coverage_configuration_by_identifier(
                session, possible_six_part_historical_cov_conf_identifier
            )
            if cov_conf is not None:
                year_period_value = parts[6]
                try:
                    year_period = HistoricalYearPeriod(year_period_value)
                except ValueError:
                    pass
                else:
                    if len(parts) > 8:
                        decade_value = parts[7]
                        try:
                            decade = HistoricalDecade(decade_value)
                        except ValueError:
                            pass
            else:
                logger.debug("could not find a cov conf with the six-part id")
        if year_period is not None:
            result = HistoricalCoverageInternal(
                configuration=cov_conf,
                year_period=year_period,
                decade=decade,
            )
    return result


def legacy_list_historical_coverages(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    name_filter: list[str] | None = None,
    conf_param_filter: Optional[LegacyConfParamFilterValues] = None,
) -> tuple[list[HistoricalCoverageInternal], Optional[int]]:
    all_cov_confs = legacy_collect_all_historical_coverage_configurations(
        session, conf_param_filter=conf_param_filter
    )
    result = []
    for cov_conf in all_cov_confs:
        result.extend(generate_historical_coverages_from_configuration(cov_conf))
    if name_filter is not None:
        for fragment in name_filter:
            result = [fc for fc in result if fragment in fc.identifier]
    return result[offset : offset + limit], len(result) if include_total else None


def list_historical_coverages(
    session: sqlmodel.Session,
    *,
    climatological_variable_filter: Optional[list[str]] = None,
    aggregation_period_filter: Optional[list[AggregationPeriod]] = None,
    measure_filter: Optional[list[MeasureType]] = None,
    year_period_filter: Optional[list[HistoricalYearPeriod]] = None,
    reference_period_filter: Optional[list[HistoricalReferencePeriod]] = None,
    decade_filter: Optional[list[HistoricalDecade]] = None,
    limit: Optional[int] = 20,
    offset: Optional[int] = 0,
    include_total: bool = False,
) -> tuple[list[HistoricalCoverageInternal], int]:
    logger.debug(f"{climatological_variable_filter=}")
    logger.debug(f"{aggregation_period_filter=}")
    logger.debug(f"{measure_filter=}")
    logger.debug(f"{year_period_filter=}")
    climatic_indicators = collect_all_climatic_indicators(
        session,
        name_filter=climatological_variable_filter,
        aggregation_period_filter=aggregation_period_filter,
        measure_type_filter=measure_filter,
    )
    logger.debug(f"{[ci.identifier for ci in climatic_indicators]=}")
    relevant_indicators = []
    for climatic_indicator in climatic_indicators:
        is_eligible = True
        if (
            climatological_variable_filter
            and climatic_indicator.name not in climatological_variable_filter
        ):
            is_eligible = False
        if measure_filter and climatic_indicator.measure_type not in measure_filter:
            is_eligible = False
        if (
            aggregation_period_filter
            and climatic_indicator.aggregation_period not in aggregation_period_filter
        ):
            is_eligible = False
        if is_eligible:
            relevant_indicators.append(climatic_indicator)
    logger.debug(f"{[ci.identifier for ci in relevant_indicators]=}")
    result = []
    if len(relevant_indicators) > 0:
        for climatic_indicator in relevant_indicators:
            cov_confs = collect_all_historical_coverage_configurations(
                session,
                climatic_indicator_filter=climatic_indicator,
                year_period_filter=year_period_filter,
                reference_period_filter=reference_period_filter,
                decade_filter=decade_filter,
            )
            for cov_conf in cov_confs:
                candidates = generate_historical_coverages_from_configuration(cov_conf)
                for candidate in candidates:
                    is_eligible = True
                    if (
                        reference_period_filter
                        and candidate.configuration.reference_period
                        not in reference_period_filter
                    ):
                        logger.debug(
                            f"\t\tReference period {candidate.configuration.reference_period} outside of filter {reference_period_filter}"
                        )
                        is_eligible = False
                    if decade_filter and candidate.decade not in decade_filter:
                        logger.debug(
                            f"\t\tDecade {candidate.decade} outside of filter {decade_filter}"
                        )
                        is_eligible = False
                    if (
                        year_period_filter
                        and candidate.year_period not in year_period_filter
                    ):
                        logger.debug(
                            f"\t\tYear period {candidate.year_period} outside of filter {year_period_filter}"
                        )
                        is_eligible = False
                    if is_eligible:
                        result.append(candidate)
    return result[offset : offset + limit], len(result) if include_total else None


def collect_all_historical_coverages(
    session: sqlmodel.Session,
    *,
    climatological_variable_filter: Optional[list[str]] = None,
    aggregation_period_filter: Optional[list[AggregationPeriod]] = None,
    measure_filter: Optional[list[MeasureType]] = None,
    year_period_filter: Optional[list[HistoricalYearPeriod]] = None,
    reference_period_filter: Optional[list[HistoricalReferencePeriod]] = None,
    decade_filter: Optional[list[HistoricalDecade]] = None,
):
    _, num_total = list_historical_coverages(
        session,
        limit=1,
        include_total=True,
        climatological_variable_filter=climatological_variable_filter,
        aggregation_period_filter=aggregation_period_filter,
        measure_filter=measure_filter,
        year_period_filter=year_period_filter,
        reference_period_filter=reference_period_filter,
        decade_filter=decade_filter,
    )
    result, _ = list_historical_coverages(
        session,
        limit=num_total,
        include_total=False,
        climatological_variable_filter=climatological_variable_filter,
        aggregation_period_filter=aggregation_period_filter,
        measure_filter=measure_filter,
        year_period_filter=year_period_filter,
        reference_period_filter=reference_period_filter,
        decade_filter=decade_filter,
    )
    return result


def list_historical_year_period_groups(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    name_filter: Optional[Union[list[str], str]] = None,
    perform_exact_matches: bool = False,
    include_total: bool = False,
) -> tuple[Sequence[HistoricalYearPeriodGroup], Optional[int]]:
    """List existing historical year period groups."""
    statement = sqlmodel.select(HistoricalYearPeriodGroup).order_by(
        HistoricalYearPeriodGroup.sort_order  # noqa
    )
    if name_filter is not None:
        if perform_exact_matches:
            statement = add_multiple_values_filter(
                statement,
                name_filter,
                HistoricalYearPeriodGroup.name,  # noqa
            )
        else:
            statement = add_substring_filter(
                statement,
                name_filter,
                HistoricalYearPeriodGroup.name,  # noqa
            )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_historical_year_period_groups(
    session: sqlmodel.Session,
    *,
    name_filter: Optional[Union[list[str], str]] = None,
    perform_exact_matches: bool = False,
):
    _, num_total = list_historical_year_period_groups(
        session,
        limit=1,
        name_filter=name_filter,
        perform_exact_matches=perform_exact_matches,
        include_total=True,
    )
    result, _ = list_historical_year_period_groups(
        session,
        limit=num_total,
        name_filter=name_filter,
        perform_exact_matches=perform_exact_matches,
        include_total=False,
    )
    return result


def get_historical_year_period_group(
    session: sqlmodel.Session, historical_year_period_group_id: int
) -> Optional[HistoricalYearPeriodGroup]:
    return session.get(HistoricalYearPeriodGroup, historical_year_period_group_id)


def get_historical_year_period_group_by_name(
    session: sqlmodel.Session, name: str
) -> Optional[HistoricalYearPeriodGroup]:
    return session.exec(
        sqlmodel.select(HistoricalYearPeriodGroup).where(  # noqa
            HistoricalYearPeriodGroup.name == name  # noqa
        )
    ).first()


def create_historical_year_period_group(
    session: sqlmodel.Session,
    historical_year_period_group_create: HistoricalYearPeriodGroupCreate,
) -> HistoricalYearPeriodGroup:
    db_group = HistoricalYearPeriodGroup(
        **historical_year_period_group_create.model_dump()
    )
    session.add(db_group)
    session.commit()
    session.refresh(db_group)
    return db_group


def update_historical_year_period_group(
    session: sqlmodel.Session,
    db_historical_year_period_group: HistoricalYearPeriodGroup,
    historical_year_period_group_update: HistoricalYearPeriodGroupUpdate,
) -> HistoricalYearPeriodGroup:
    data_ = historical_year_period_group_update.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )
    for key, value in data_.items():
        setattr(db_historical_year_period_group, key, value)
    session.add(db_historical_year_period_group)
    session.commit()
    session.refresh(db_historical_year_period_group)
    return db_historical_year_period_group


def delete_historical_year_period_group(
    session: sqlmodel.Session, historical_year_period_group_id: int
) -> None:
    db_item = get_historical_year_period_group(session, historical_year_period_group_id)
    if db_item is not None:
        session.delete(db_item)
        session.commit()
    else:
        raise RuntimeError("Historical year period group not found")
