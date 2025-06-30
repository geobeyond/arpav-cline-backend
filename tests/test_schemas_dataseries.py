from contextlib import nullcontext

import pydantic
import pytest

from arpav_cline.schemas import dataseries


@pytest.mark.parametrize(
    "start, end, expected",
    [
        pytest.param(
            None,
            None,
            nullcontext(
                dataseries.MannKendallParameters(start_year=None, end_year=None)
            ),
        ),
        pytest.param(
            None,
            1990,
            nullcontext(
                dataseries.MannKendallParameters(start_year=None, end_year=1990)
            ),
        ),
        pytest.param(
            1990,
            None,
            nullcontext(
                dataseries.MannKendallParameters(start_year=1990, end_year=None)
            ),
        ),
        pytest.param(
            2000,
            2027,
            nullcontext(
                dataseries.MannKendallParameters(start_year=2000, end_year=2027)
            ),
        ),
        pytest.param(
            2001,
            2027,
            pytest.raises(pydantic.ValidationError),
            id="year span less than 27 years",
        ),
    ],
)
def test_mann_kendall_parameters_year_span(start, end, expected):
    with expected as e:
        result = dataseries.MannKendallParameters(
            start_year=start,
            end_year=end,
        )
        assert result == e
