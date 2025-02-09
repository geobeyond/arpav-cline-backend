import itertools
from typing import (
    Optional,
    Sequence,
)

import sqlmodel

from .. import (
    database,
    exceptions,
)
from ..schemas.base import SpatialRegion
from ..schemas import (
    climaticindicators,
    coverages,
    static,
)
from .base import get_total_num_records


def list_historical_coverage_configurations(
    session: sqlmodel.Session,
    *,
    limit: int = 20,
    offset: int = 0,
    include_total: bool = False,
    climatic_indicator_name_filter: Optional[str] = None,
    climatic_indicator_filter: Optional[climaticindicators.ClimaticIndicator] = None,
) -> tuple[Sequence[coverages.HistoricalCoverageConfiguration], Optional[int]]:
    """List existing historical coverage configurations."""
    statement = sqlmodel.select(coverages.HistoricalCoverageConfiguration).order_by(
        coverages.HistoricalCoverageConfiguration.id
    )
    if climatic_indicator_filter is not None:
        statement = statement.where(
            coverages.HistoricalCoverageConfiguration.climatic_indicator_id
            == climatic_indicator_filter.id
        )
    if climatic_indicator_name_filter is not None:
        filter_ = climatic_indicator_name_filter.replace("%", "")
        filter_ = f"%{filter_}%"
        statement = statement.join(
            climaticindicators.ClimaticIndicator,
            climaticindicators.ClimaticIndicator.id
            == coverages.HistoricalCoverageConfiguration.climatic_indicator_id,
            ).where(climaticindicators.ClimaticIndicator.name.ilike(filter_))
    items = session.exec(statement.offset(offset).limit(limit)).all()
    num_items = get_total_num_records(session, statement) if include_total else None
    return items, num_items


def collect_all_historical_coverage_configurations(
    session: sqlmodel.Session,
    climatic_indicator_name_filter: Optional[str] = None,
    climatic_indicator_filter: Optional[climaticindicators.ClimaticIndicator] = None,
) -> Sequence[coverages.HistoricalCoverageConfiguration]:
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
) -> list[coverages.HistoricalCoverageConfiguration]:
    all_hccs = collect_all_historical_coverage_configurations(session)
    if identifier_filter is not None:
        result = [hcc for hcc in all_hccs if identifier_filter in hcc.identifier]
    else:
        result = all_hccs
    return result


def get_historical_coverage_configuration(
    session: sqlmodel.Session,
    historical_coverage_configuration_id: int,
) -> Optional[coverages.HistoricalCoverageConfiguration]:
    return session.get(
        coverages.HistoricalCoverageConfiguration, historical_coverage_configuration_id
    )


def get_historical_coverage_configuration_by_identifier(
    session: sqlmodel.Session, identifier: str
) -> Optional[coverages.HistoricalCoverageConfiguration]:
    error_message = f"{identifier!r} is not a valid historical coverage identifier"
    parts = identifier.split("-")
    if parts[0] == static.DataCategory.HISTORICAL.value:
        if len(parts) >= 5:
            climatic_indicator_identifier = "-".join(parts[1:4])
            climatic_indicator = database.get_climatic_indicator_by_identifier(
                session, climatic_indicator_identifier
            )
            if climatic_indicator is None:
                raise exceptions.InvalidClimaticIndicatorIdentifierError(
                    f"{climatic_indicator_identifier!r} is not a valid climatic "
                    f"indicator identifier"
                )
            spatial_region_name = parts[4]
            spatial_region = database.get_spatial_region_by_name(
                session, spatial_region_name)
            if spatial_region is None:
                raise exceptions.InvalidSpatialRegionNameError(
                    f"{spatial_region_name!r} is not a valid spatial region name"
                )

            if len(parts) == 5:
                result = _get_five_part_hcc(session, climatic_indicator, spatial_region)
            elif len(parts) == 6:
                try:
                    reference_period = static.HistoricalReferencePeriod(parts[5])
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
    climatic_indicator: climaticindicators.ClimaticIndicator,
    spatial_region: SpatialRegion,
) -> Optional[coverages.HistoricalCoverageConfiguration]:
    statement = sqlmodel.select(coverages.HistoricalCoverageConfiguration).where(
        coverages.HistoricalCoverageConfiguration.climatic_indicator_id
        == climatic_indicator.id,
        coverages.HistoricalCoverageConfiguration.spatial_region_id == spatial_region.id,
        )
    return session.exec(statement).first()


def _get_six_part_hcc(
    session: sqlmodel.Session,
    climatic_indicator: climaticindicators.ClimaticIndicator,
    spatial_region: SpatialRegion,
    reference_period: static.HistoricalReferencePeriod,
) -> Optional[coverages.HistoricalCoverageConfiguration]:
    """Try to find a historical coverage identifier made up of six parts."""
    statement = sqlmodel.select(coverages.HistoricalCoverageConfiguration).where(
        coverages.HistoricalCoverageConfiguration.climatic_indicator_id
        == climatic_indicator.id,
        coverages.HistoricalCoverageConfiguration.spatial_region_id == spatial_region.id,
        )
    result = None
    statement = statement.where(
        reference_period.name == coverages.HistoricalCoverageConfiguration.reference_period
    )
    return session.exec(statement).first()


def create_historical_coverage_configuration(
    session: sqlmodel.Session,
    historical_coverage_configuration_create: coverages.HistoricalCoverageConfigurationCreate,
) -> coverages.HistoricalCoverageConfiguration:
    db_historical_coverage_configuration = coverages.HistoricalCoverageConfiguration(
        **historical_coverage_configuration_create.model_dump()
    )
    session.add(db_historical_coverage_configuration)
    session.commit()
    session.refresh(db_historical_coverage_configuration)
    return db_historical_coverage_configuration


def update_historical_coverage_configuration(
    session: sqlmodel.Session,
    db_historical_coverage_configuration: coverages.HistoricalCoverageConfiguration,
    historical_coverage_configuration_update: coverages.HistoricalCoverageConfigurationUpdate,
) -> coverages.HistoricalCoverageConfiguration:
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
    historical_coverage_configuration: coverages.HistoricalCoverageConfiguration,
) -> list[coverages.HistoricalCoverageInternal]:
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
            coverages.HistoricalCoverageInternal(
                configuration=historical_coverage_configuration,
                year_period=year_period,
                decade=decade,
            )
        )
    return result
