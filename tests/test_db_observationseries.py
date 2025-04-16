import datetime as dt

import pytest

from arpav_cline import db
from arpav_cline.schemas.observations import ObservationMeasurementCreate
from arpav_cline.schemas.static import MeasurementAggregationType


@pytest.mark.parametrize(
    "indicator_identifier, candidate_date, candidate_aggregation_type, should_be_created",
    [
        pytest.param(
            "tas-absolute-annual",
            dt.date(1987, 1, 1),
            MeasurementAggregationType.MONTHLY,
            False,
            id="already-exists",
        ),
        pytest.param(
            "tas-absolute-annual",
            dt.date(2025, 1, 1),
            MeasurementAggregationType.MONTHLY,
            True,
            id="new-year",
        ),
        pytest.param(
            "tasmax-absolute-annual",
            dt.date(1987, 1, 1),
            MeasurementAggregationType.MONTHLY,
            True,
            id="different-indicator",
        ),
        pytest.param(
            "tas-absolute-annual",
            dt.date(1987, 1, 1),
            MeasurementAggregationType.SEASONAL,
            True,
            id="different-aggregation-type",
        ),
    ],
)
def test_find_new_station_measurements(
    arpav_db_session,
    sample_real_station,
    sample_monthly_measurements,  # noqa
    sample_real_climatic_indicators,  # noqa
    indicator_identifier,
    candidate_date,
    candidate_aggregation_type,
    should_be_created,
):
    indicator = db.get_climatic_indicator_by_identifier(
        arpav_db_session, indicator_identifier
    )
    candidates = [
        ObservationMeasurementCreate(
            value=0,
            date=candidate_date,
            measurement_aggregation_type=candidate_aggregation_type,
            observation_station_id=sample_real_station.id,
            climatic_indicator_id=indicator.id,
        )
    ]
    new_measurements = db.find_new_station_measurements(
        arpav_db_session, station_id=sample_real_station.id, candidates=candidates
    )
    if should_be_created:
        assert candidates[0] == new_measurements[0]
    else:
        assert len(new_measurements) == 0


# def test_find_new_station_measurements_prevents_duplicate_dates(
#         arpav_db_session,
#         sample_real_station,
#         sample_monthly_measurements,
#         sample_real_climatic_indicators
# ):
#     tas_absolute_annual_indicator = db.get_climatic_indicator_by_identifier(
#         arpav_db_session, "tas-absolute-annual")
#     candidates = [
#         # this date already exists in the db as it is created by the
#         # `sample_monthly_measurements` fixture
#         ObservationMeasurementCreate(
#             value=0,
#             date=dt.date(1987, 1, 1),
#             measurement_aggregation_type=MeasurementAggregationType.MONTHLY,
#             observation_station_id=sample_real_station.id,
#             climatic_indicator_id=tas_absolute_annual_indicator.id,
#         )
#     ]
#     new_measurements = db.find_new_station_measurements(
#         arpav_db_session,
#         station_id=sample_real_station.id,
#         candidates=candidates
#     )
#     assert len(new_measurements) == 0
#
#
# def test_find_new_station_measurements_distinguishes_between_different_aggregation_types(
#         arpav_db_session,
#         sample_real_station,
#         sample_monthly_measurements,
#         sample_real_climatic_indicators
# ):
#     tas_absolute_annual_indicator = db.get_climatic_indicator_by_identifier(
#         arpav_db_session, "tas-absolute-annual")
#     candidates = [
#         # this date already exists in the db as it is created by the
#         # `sample_monthly_measurements` fixture
#         ObservationMeasurementCreate(
#             value=0,
#             date=dt.date(1987, 1, 1),
#             measurement_aggregation_type=MeasurementAggregationType.YEARLY,
#             observation_station_id=sample_real_station.id,
#             climatic_indicator_id=tas_absolute_annual_indicator.id,
#         )
#     ]
#     new_measurements = db.find_new_station_measurements(
#         arpav_db_session,
#         station_id=sample_real_station.id,
#         candidates=candidates
#     )
#     for c in candidates:
#         assert c in new_measurements
