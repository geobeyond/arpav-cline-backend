import typing
import datetime as dt

from .. import exceptions
from ..schemas.static import (
    MeasurementAggregationType,
    ObservationStationManager,
    ObservationYearPeriod,
)

if typing.TYPE_CHECKING:
    from ..schemas.climaticindicators import ClimaticIndicator


def get_indicator_internal_name(
    climatic_indicator: "ClimaticIndicator",
    station_manager: ObservationStationManager,
) -> str:
    try:
        return [
            obs_name.indicator_observation_name
            for obs_name in climatic_indicator.observation_names
            if obs_name.station_manager == station_manager
        ][0]
    except IndexError as err:
        raise exceptions.ObservationInternalNameNotFoundError(
            f"Could not find an internal name for climatic indicator "
            f"{climatic_indicator.identifier!r} and station "
            f"manager {station_manager}"
        ) from err


def parse_measurement_date(
    raw_year: int,
    aggregation_type: MeasurementAggregationType,
    year_period: ObservationYearPeriod,
) -> dt.date:
    """Parse a raw measurement date.

    Dates are set to the middle of the corresponding yearly aggregation
    period. For example:

    - Winter 1991 (i.e. December 1990, January 1991, February 1991) is set to
    1st January 1991
    - All year 1991 (i.e. all months of the year) is set to 1st July 1991
    - March 1991 is set to March 15th 1991
    """

    if aggregation_type == MeasurementAggregationType.YEARLY:
        result = dt.date(raw_year, 7, 1)
    elif aggregation_type == MeasurementAggregationType.SEASONAL:
        result = {
            ObservationYearPeriod.WINTER: dt.date(raw_year, 1, 1),
            ObservationYearPeriod.SPRING: dt.date(raw_year, 4, 1),
            ObservationYearPeriod.SUMMER: dt.date(raw_year, 7, 1),
            ObservationYearPeriod.AUTUMN: dt.date(raw_year, 10, 1),
        }[year_period]
    elif aggregation_type == MeasurementAggregationType.MONTHLY:
        result = {
            ObservationYearPeriod.JANUARY: dt.date(raw_year, 1, 15),
            ObservationYearPeriod.FEBRUARY: dt.date(raw_year, 2, 15),
            ObservationYearPeriod.MARCH: dt.date(raw_year, 3, 15),
            ObservationYearPeriod.APRIL: dt.date(raw_year, 4, 15),
            ObservationYearPeriod.MAY: dt.date(raw_year, 5, 15),
            ObservationYearPeriod.JUNE: dt.date(raw_year, 6, 15),
            ObservationYearPeriod.JULY: dt.date(raw_year, 7, 15),
            ObservationYearPeriod.AUGUST: dt.date(raw_year, 8, 15),
            ObservationYearPeriod.SEPTEMBER: dt.date(raw_year, 9, 15),
            ObservationYearPeriod.OCTOBER: dt.date(raw_year, 10, 15),
            ObservationYearPeriod.NOVEMBER: dt.date(raw_year, 11, 15),
            ObservationYearPeriod.DECEMBER: dt.date(raw_year, 12, 15),
        }[year_period]
    else:
        raise NotImplementedError(
            f"aggregation type {aggregation_type!r} not implemented"
        )
    return result
