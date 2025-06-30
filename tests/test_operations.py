import datetime as dt

import pytest

from arpav_cline import operations
from arpav_cline.schemas import static
from arpav_cline.schemas.climaticindicators import ClimaticIndicator
from arpav_cline.schemas.coverages import ForecastTimeWindow


@pytest.mark.parametrize(
    "temporal_range, expected",
    [
        pytest.param("../..", (None, None)),
        pytest.param(
            "1982-12-10T01:01:00Z/..",
            (dt.datetime(1982, 12, 10, 1, 1, 0, tzinfo=dt.timezone.utc), None),
        ),
        pytest.param(
            "1982-12-10T01:01:00+01:00/..",
            (dt.datetime(1982, 12, 10, 0, 1, 0, tzinfo=dt.timezone.utc), None),
        ),
        pytest.param(
            "1982-12-10T01:01:00+02:00/..",
            (dt.datetime(1982, 12, 9, 23, 1, 0, tzinfo=dt.timezone.utc), None),
        ),
    ],
)
def test_parse_temporal_range(temporal_range, expected):
    result = operations.parse_temporal_range(temporal_range)  # noqa
    assert result == expected


@pytest.mark.parametrize(
    "values, expected",
    [
        pytest.param(
            ["aggregation_period:30yr"],
            {"aggregation_period": static.AggregationPeriod.THIRTY_YEAR},
        ),
        pytest.param(
            ["aggregation_period:thirty_year"],
            {"aggregation_period": static.AggregationPeriod.THIRTY_YEAR},
        ),
        pytest.param(["archive:forecast"], {"archive": "forecast"}),
        pytest.param(
            ["climatological_model:model_ensemble"],
            {"climatological_model": "model_ensemble"},
        ),
        pytest.param(
            ["climatological_variable:tas"], {"climatological_variable": "tas"}
        ),
        pytest.param(
            ["historical_decade:decade_1991_2000"],
            {"historical_decade": static.HistoricalDecade.DECADE_1991_2000},
        ),
        pytest.param(
            ["historical_reference_period:climate_standard_normal_1961_1990"],
            {
                "historical_reference_period": static.HistoricalReferencePeriod.CLIMATE_STANDARD_NORMAL_1961_1990
            },
        ),
        pytest.param(
            ["historical_year_period:winter"],
            {"historical_year_period": static.HistoricalYearPeriod.WINTER},
        ),
        pytest.param(["measure:absolute"], {"measure": static.MeasureType.ABSOLUTE}),
        pytest.param(["scenario:rcp26"], {"scenario": static.ForecastScenario.RCP26}),
        pytest.param(
            ["uncertainty_type:lower_uncertainty"],
            {"uncertainty_type": "lower_uncertainty"},
        ),
        pytest.param(["time_window:tw1"], {"time_window": "tw1"}),
        pytest.param(
            ["year_period:summer"], {"year_period": static.ForecastYearPeriod.SUMMER}
        ),
        pytest.param(
            ["historical_decade:decade_1991_2000", "climatological_variable:tas"],
            {
                "historical_decade": static.HistoricalDecade.DECADE_1991_2000,
                "climatological_variable": "tas",
            },
        ),
    ],
)
def test_convert_conf_params_filter(
    arpav_db_session,
    sample_real_climatic_indicators: list[ClimaticIndicator],
    sample_real_forecast_time_windows: list[ForecastTimeWindow],
    values: list[str],
    expected,
):
    result = operations.convert_conf_params_filter(arpav_db_session, values)
    for key, expected_value in expected.items():
        if key == "climatological_model":
            assert result.climatological_model.name == expected_value
        elif key == "time_window":
            assert result.time_window.name == expected_value
        else:
            assert getattr(result, key) == expected_value
