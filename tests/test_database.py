from operator import attrgetter

import pytest

from arpav_ppcv import db
from arpav_ppcv.schemas import static


@pytest.mark.parametrize(
    "limit, offset, include_total",
    [
        pytest.param(10, 0, False),
        pytest.param(10, 0, True),
        pytest.param(20, 20, True),
    ],
)
def test_list_stations(arpav_db_session, sample_stations, limit, offset, include_total):
    ordered_stations = sorted(sample_stations, key=lambda station: station.code)
    expected_codes = [s.code for s in ordered_stations][offset : offset + limit]
    db_stations, total = db.list_observation_stations(
        arpav_db_session, limit=limit, offset=offset, include_total=include_total
    )
    if include_total:
        assert total == len(sample_stations)
    else:
        assert total is None
    for index, db_station in enumerate(db_stations):
        assert db_station.code == expected_codes[index]


@pytest.mark.parametrize(
    "limit, offset, include_total",
    [
        pytest.param(10, 0, False),
        pytest.param(10, 0, True),
        pytest.param(5, 2, True),
    ],
)
def test_list_climatic_indicators(
    arpav_db_session, sample_real_climatic_indicators, limit, offset, include_total
):
    ordered_indicators = sorted(
        sample_real_climatic_indicators,
        key=attrgetter("sort_order", "name", "aggregation_period", "measure_type"),
    )
    expected_identifiers = [i.identifier for i in ordered_indicators][
        offset : offset + limit
    ]
    db_climatic_indicators, total = db.list_climatic_indicators(
        arpav_db_session, limit=limit, offset=offset, include_total=include_total
    )
    if include_total:
        assert total == len(sample_real_climatic_indicators)
    else:
        assert total is None
    for index, db_climatic_indicator in enumerate(db_climatic_indicators):
        assert db_climatic_indicator.identifier == expected_identifiers[index]


@pytest.mark.parametrize(
    "limit, offset, include_total",
    [
        pytest.param(20, 0, False),
        pytest.param(20, 0, True),
        pytest.param(20, 20, True),
    ],
)
def test_list_monthly_measurements(
    arpav_db_session, sample_monthly_measurements, limit, offset, include_total
):
    ordered_measurements = sorted(sample_monthly_measurements, key=lambda m: m.date)
    expected_dates = [m.date for m in ordered_measurements][offset : offset + limit]
    db_measurements, total = db.list_observation_measurements(
        arpav_db_session,
        limit=limit,
        offset=offset,
        include_total=include_total,
        aggregation_type_filter=static.MeasurementAggregationType.MONTHLY,
    )
    if include_total:
        assert total == len(sample_monthly_measurements)
    else:
        assert total is None
    for index, db_measurement in enumerate(db_measurements):
        assert db_measurement.date == expected_dates[index]
