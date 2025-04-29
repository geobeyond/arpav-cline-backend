from contextlib import nullcontext

import pytest

from arpav_cline import timeseries
from arpav_cline.exceptions import MannKendallInsufficientYearError
from arpav_cline.schemas import static


@pytest.mark.parametrize(
    "position_index, mk_start, mk_end, expected",
    [
        pytest.param(
            slice(0, 30),
            None,
            None,
            nullcontext({"start": 1976, "end": 2005, "m": 0.02695420, "b": 3.36297259}),
        ),
        pytest.param(
            slice(0, 26), None, None, pytest.raises(MannKendallInsufficientYearError)
        ),
        pytest.param(
            slice(0, 30, 3), None, None, pytest.raises(MannKendallInsufficientYearError)
        ),
        pytest.param(
            None,
            1980,
            None,
            nullcontext({"start": 1980, "end": 2017, "m": 0.01902530, "b": 3.54188550}),
        ),
        pytest.param(
            None,
            None,
            2010,
            nullcontext({"start": 1976, "end": 2010, "m": 0.03325679, "b": 3.31048281}),
        ),
        pytest.param(
            None,
            1980,
            2010,
            nullcontext({"start": 1980, "end": 2010, "m": 0.03479485, "b": 3.35392543}),
        ),
    ],
)
def test_generate_mann_kendall_derived_historical_coverage_series(
    sample_tas_historical_data_series,
    position_index,
    mk_start,
    mk_end,
    expected,
):
    if position_index is not None:
        pd_series = sample_tas_historical_data_series.data_.copy(deep=True)
        sample_tas_historical_data_series.data_ = pd_series.iloc[position_index]
    with expected as e:
        result = timeseries.generate_mann_kendall_derived_historical_coverage_series(
            sample_tas_historical_data_series, start_year=mk_start, end_year=mk_end
        )
        print(result)
        assert (
            result.processing_method
            == static.HistoricalTimeSeriesProcessingMethod.MANN_KENDALL_TREND
        )
        assert result.location == sample_tas_historical_data_series.location
        assert result.processing_method_info["start_year"] == e["start"]
        assert result.processing_method_info["end_year"] == e["end"]
        assert result.processing_method_info["slope"] == pytest.approx(e["m"])
        assert result.processing_method_info["intercept"] == pytest.approx(e["b"])
