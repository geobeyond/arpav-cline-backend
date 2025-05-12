import datetime as dt

import pytest

from arpav_cline.observations_harvester import common
from arpav_cline.schemas.static import MeasurementAggregationType, ObservationYearPeriod


@pytest.mark.parametrize(
    "raw_year, aggregation_type, year_period, expected",
    [
        pytest.param(
            1991,
            MeasurementAggregationType.SEASONAL,
            ObservationYearPeriod.AUTUMN,
            dt.date(1991, 10, 1),
        ),
        pytest.param(
            1991,
            MeasurementAggregationType.MONTHLY,
            ObservationYearPeriod.OCTOBER,
            dt.date(1991, 10, 15),
        ),
        pytest.param(
            1991,
            MeasurementAggregationType.YEARLY,
            ObservationYearPeriod.ALL_YEAR,
            dt.date(1991, 7, 1),
        ),
    ],
)
def test_parse_measurement_date(raw_year, aggregation_type, year_period, expected):
    result = common.parse_measurement_date(raw_year, aggregation_type, year_period)
    assert result == expected
