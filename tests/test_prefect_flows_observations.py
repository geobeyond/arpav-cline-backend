import datetime as dt
import uuid

import pytest

from arpav_ppcv.prefect.flows import observations
from arpav_ppcv.schemas import observations as observation_schemas
from arpav_ppcv.schemas.base import Season


@pytest.mark.parametrize(
    "station_id, climatic_indicator_id, value, date, expected",
    [
        pytest.param(
            uuid.UUID("65af54f0-1df2-423b-994f-03fa1195dd7b"),
            1,
            10.23,
            dt.date(2020, 1, 1),
            "65af54f0-1df2-423b-994f-03fa1195dd7b-1-202001",
        ),
    ],
)
def test_build_monthly_measurement_id(
    station_id, climatic_indicator_id, value, date, expected
):
    result = observations.build_monthly_measurement_id(
        observation_schemas.MonthlyMeasurementCreate(
            station_id=station_id,
            climatic_indicator_id=climatic_indicator_id,
            value=value,
            date=date,
        )
    )
    assert result == expected


@pytest.mark.parametrize(
    "station_id, climatic_indicator_id, value, year, season, expected",
    [
        pytest.param(
            uuid.UUID("65af54f0-1df2-423b-994f-03fa1195dd7b"),
            2,
            10.23,
            2020,
            Season.SUMMER,
            "65af54f0-1df2-423b-994f-03fa1195dd7b-2-2020-SUMMER",
        ),
    ],
)
def test_build_seasonal_measurement_id(
    station_id, climatic_indicator_id, value, year, season, expected
):
    result = observations.build_seasonal_measurement_id(
        observation_schemas.SeasonalMeasurementCreate(
            station_id=station_id,
            climatic_indicator_id=climatic_indicator_id,
            value=value,
            year=year,
            season=season,
        )
    )
    assert result == expected


@pytest.mark.parametrize(
    "station_id, climatic_indicator_id, value, year, expected",
    [
        pytest.param(
            uuid.UUID("65af54f0-1df2-423b-994f-03fa1195dd7b"),
            3,
            10.23,
            2020,
            "65af54f0-1df2-423b-994f-03fa1195dd7b-3-2020",
        ),
    ],
)
def test_build_yearly_measurement_id(
    station_id, climatic_indicator_id, value, year, expected
):
    result = observations.build_yearly_measurement_id(
        observation_schemas.YearlyMeasurementCreate(
            station_id=station_id,
            climatic_indicator_id=climatic_indicator_id,
            value=value,
            year=year,
        )
    )
    assert result == expected
