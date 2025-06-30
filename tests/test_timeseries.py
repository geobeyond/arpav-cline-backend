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


@pytest.mark.parametrize(
    "mk_start, mk_end, expected",
    [
        pytest.param(1970, 2000, pytest.raises(MannKendallInsufficientYearError)),
        pytest.param(2000, 2027, pytest.raises(MannKendallInsufficientYearError)),
        pytest.param(1970, 2010, nullcontext({"start": 1976, "end": 2010})),
        pytest.param(1980, 2010, nullcontext({"start": 1980, "end": 2010})),
    ],
)
def test_generate_mann_kendall_series_year_span(
    sample_tas_historical_data_series,
    mk_start,
    mk_end,
    expected,
):
    df = sample_tas_historical_data_series.data_.copy(deep=True).to_frame()
    target_name = "fake_name"
    with expected as e:
        mk_df, info = timeseries._generate_mann_kendall_series(
            original=df,
            original_column=sample_tas_historical_data_series.data_.name,
            column_name=target_name,
            start_year=mk_start,
            end_year=mk_end,
        )
        assert e["start"] == info["start_year"]
        assert e["end"] == info["end_year"]


def test_generate_decade_series(
    sample_tas_historical_data_series,
):
    target_name = "fake_name"
    df = sample_tas_historical_data_series.data_.copy(deep=True).to_frame()
    result = timeseries._generate_decade_series(
        df, sample_tas_historical_data_series.data_.name, target_name
    )
    expected = (
        "time,{variable_name}\n"
        "1981-01-01 00:00:00+00:00,3.5072722599999997\n1982-01-01 00:00:00+00:00,3.5072722599999997\n1983-01-01 00:00:00+00:00,3.5072722599999997\n"
        "1984-01-01 00:00:00+00:00,3.5072722599999997\n1985-01-01 00:00:00+00:00,3.5072722599999997\n1986-01-01 00:00:00+00:00,3.5072722599999997\n"
        "1987-01-01 00:00:00+00:00,3.5072722599999997\n1988-01-01 00:00:00+00:00,3.5072722599999997\n1989-01-01 00:00:00+00:00,3.5072722599999997\n"
        "1990-01-01 00:00:00+00:00,3.5072722599999997\n"
        "1991-01-01 00:00:00+00:00,3.9813628199999997\n1992-01-01 00:00:00+00:00,3.9813628199999997\n1993-01-01 00:00:00+00:00,3.9813628199999997\n"
        "1994-01-01 00:00:00+00:00,3.9813628199999997\n1995-01-01 00:00:00+00:00,3.9813628199999997\n1996-01-01 00:00:00+00:00,3.9813628199999997\n"
        "1997-01-01 00:00:00+00:00,3.9813628199999997\n1998-01-01 00:00:00+00:00,3.9813628199999997\n1999-01-01 00:00:00+00:00,3.9813628199999997\n"
        "2000-01-01 00:00:00+00:00,3.9813628199999997\n"
        "2001-01-01 00:00:00+00:00,4.23422232\n2002-01-01 00:00:00+00:00,4.23422232\n2003-01-01 00:00:00+00:00,4.23422232\n"
        "2004-01-01 00:00:00+00:00,4.23422232\n2005-01-01 00:00:00+00:00,4.23422232\n2006-01-01 00:00:00+00:00,4.23422232\n"
        "2007-01-01 00:00:00+00:00,4.23422232\n2008-01-01 00:00:00+00:00,4.23422232\n2009-01-01 00:00:00+00:00,4.23422232\n"
        "2010-01-01 00:00:00+00:00,4.23422232\n"
        "2011-01-01 00:00:00+00:00,3.828210342857143\n2012-01-01 00:00:00+00:00,3.828210342857143\n2013-01-01 00:00:00+00:00,3.828210342857143\n"
        "2014-01-01 00:00:00+00:00,3.828210342857143\n2015-01-01 00:00:00+00:00,3.828210342857143\n2016-01-01 00:00:00+00:00,3.828210342857143\n"
        "2017-01-01 00:00:00+00:00,3.828210342857143\n2018-01-01 00:00:00+00:00,3.828210342857143\n2019-01-01 00:00:00+00:00,3.828210342857143\n"
        "2020-01-01 00:00:00+00:00,3.828210342857143\n"
    )
    assert result[target_name].to_csv() == expected.format(variable_name=target_name)
