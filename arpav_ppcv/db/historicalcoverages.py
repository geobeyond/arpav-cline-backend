import itertools
import logging
from typing import (
    Optional,
    Sequence,
)

import sqlmodel

from .. import exceptions
from ..schemas.base import SpatialRegion
from ..schemas.climaticindicators import (
    ClimaticIndicator,
)
from ..schemas.coverages import (
    HistoricalCoverageInternal,
    HistoricalCoverageConfiguration,
    HistoricalCoverageConfigurationCreate,
    HistoricalCoverageConfigurationUpdate,
    LegacyConfParamFilterValues,
)
from ..schemas.static import (
    DataCategory,
    HistoricalReferencePeriod,
    HistoricalYearPeriod,
    HistoricalDecade,
)
from .base import (
    add_substring_filter,
    get_total_num_records,
)
from .climaticindicators import get_climatic_indicator_by_identifier
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
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_historical_coverage_configurations(
    session: sqlmodel.Session,
    climatic_indicator_name_filter: Optional[str] = None,
    climatic_indicator_filter: Optional[ClimaticIndicator] = None,
) -> Sequence[HistoricalCoverageConfiguration]:
    _, num_total = list_historical_coverage_configurations(
        session,
        limit=1,
        include_total=True,
        climatic_indicator_name_filter=climatic_indicator_name_filter,
        climatic_indicator_filter=climatic_indicator_filter,
    )
    result, _ = list_historical_coverage_configurations(
        session,
        limit=num_total,
        include_total=False,
        climatic_indicator_name_filter=climatic_indicator_name_filter,
        climatic_indicator_filter=climatic_indicator_filter,
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
    error_message = f"{identifier!r} is not a valid historical coverage identifier"
    parts = identifier.split("-")
    if parts[0] == DataCategory.HISTORICAL.value:
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
                result = _get_five_part_hcc(session, climatic_indicator, spatial_region)
            elif len(parts) == 6:
                try:
                    reference_period = HistoricalReferencePeriod(parts[5])
                except ValueError:
                    raise exceptions.InvalidHistoricalCoverageConfigurationIdentifierError(
                        error_message + "- invalid reference period"
                    )
                result = _get_six_part_hcc(
                    session, climatic_indicator, spatial_region, reference_period
                )
            else:
                raise exceptions.InvalidHistoricalCoverageConfigurationIdentifierError(
                    error_message + "- identifier is too long"
                )
            return result
        else:
            raise exceptions.InvalidHistoricalCoverageConfigurationIdentifierError(
                error_message + "- identifier is too short"
            )
    else:
        raise exceptions.InvalidHistoricalCoverageConfigurationIdentifierError(
            error_message
        )


def _get_five_part_hcc(
    session: sqlmodel.Session,
    climatic_indicator: ClimaticIndicator,
    spatial_region: SpatialRegion,
) -> Optional[HistoricalCoverageConfiguration]:
    statement = sqlmodel.select(HistoricalCoverageConfiguration).where(
        HistoricalCoverageConfiguration.climatic_indicator_id == climatic_indicator.id,
        HistoricalCoverageConfiguration.spatial_region_id == spatial_region.id,
    )
    query_result = session.exec(statement).all()
    result = None
    for hcc in query_result:
        if len(hcc.identifier.split("-")) == 5:
            result = hcc
            break
    return result


def _get_six_part_hcc(
    session: sqlmodel.Session,
    climatic_indicator: ClimaticIndicator,
    spatial_region: SpatialRegion,
    reference_period: HistoricalReferencePeriod,
) -> Optional[HistoricalCoverageConfiguration]:
    """Try to find a historical coverage identifier made up of six parts."""
    statement = sqlmodel.select(HistoricalCoverageConfiguration).where(
        HistoricalCoverageConfiguration.climatic_indicator_id == climatic_indicator.id,
        HistoricalCoverageConfiguration.spatial_region_id == spatial_region.id,
        reference_period.name == HistoricalCoverageConfiguration.reference_period,
    )
    return session.exec(statement).first()


def create_historical_coverage_configuration(
    session: sqlmodel.Session,
    historical_coverage_configuration_create: HistoricalCoverageConfigurationCreate,
) -> HistoricalCoverageConfiguration:
    db_historical_coverage_configuration = HistoricalCoverageConfiguration(
        **historical_coverage_configuration_create.model_dump()
    )
    session.add(db_historical_coverage_configuration)
    session.commit()
    session.refresh(db_historical_coverage_configuration)
    return db_historical_coverage_configuration


def update_historical_coverage_configuration(
    session: sqlmodel.Session,
    db_historical_coverage_configuration: HistoricalCoverageConfiguration,
    historical_coverage_configuration_update: HistoricalCoverageConfigurationUpdate,
) -> HistoricalCoverageConfiguration:
    """Update a historical coverage configuration."""
    data_ = historical_coverage_configuration_update.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )
    for key, value in data_.items():
        setattr(db_historical_coverage_configuration, key, value)
    session.add(db_historical_coverage_configuration)
    session.commit()
    session.refresh(db_historical_coverage_configuration)
    return db_historical_coverage_configuration


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
        historical_coverage_configuration.year_periods,
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
            statement = statement.where(
                conf_param_filter.historical_decade.name
                == sqlalchemy.any_(HistoricalCoverageConfiguration.year_periods)  # noqa
            )
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def get_historical_coverage(
    session: sqlmodel.Session, identifier: str
) -> Optional[HistoricalCoverageInternal]:
    parts = identifier.split("-")
    result = None
    historical_cov_conf = None
    year_period = None
    decade = None
    # historical cov conf has either 5 or 6 parts, then we have the year period and maybe a decade
    if len(parts) >= 6:
        possible_six_part_cov_conf_identifier = "-".join((parts[:6]))
        try:
            historical_cov_conf = get_historical_coverage_configuration_by_identifier(
                session, possible_six_part_cov_conf_identifier
            )
        except exceptions.ArpavError:
            logger.info(
                f"Could not extract six-part historical coverage configuration "
                f"from {possible_six_part_cov_conf_identifier!r}"
            )

        if historical_cov_conf is not None:
            try:
                year_period = HistoricalYearPeriod(parts[6])
            except ValueError:
                logger.warning(
                    f"Could not extract historical year period from {parts[6]!r}"
                )
            try:
                decade = HistoricalDecade(parts[7]) if len(parts) > 7 else None
            except ValueError:
                logger.warning(f"Could not extract historical decade from {parts[7]!r}")
        else:
            possible_five_part_cov_conf_identifier = "-".join((parts[:5]))
            try:
                historical_cov_conf = (
                    get_historical_coverage_configuration_by_identifier(
                        session, possible_five_part_cov_conf_identifier
                    )
                )
            except exceptions.ArpavError:
                logger.info(
                    f"Could not extract five-part historical coverage configuration "
                    f"from {possible_five_part_cov_conf_identifier!r}"
                )

            if historical_cov_conf is not None:
                try:
                    year_period = HistoricalYearPeriod(parts[5])
                except ValueError:
                    logger.warning(
                        f"Could not extract historical year period from {parts[5]!r}"
                    )
                try:
                    decade = HistoricalDecade(parts[6]) if len(parts) > 6 else None
                except ValueError:
                    logger.warning(
                        f"Could not extract historical decade from {parts[6]!r}"
                    )
        if all((historical_cov_conf, year_period)):
            result = HistoricalCoverageInternal(
                configuration=historical_cov_conf,
                year_period=year_period,
                decade=decade,
            )
    else:
        logger.warning("Identifier is too short to represent a historical coverage")
    return result
