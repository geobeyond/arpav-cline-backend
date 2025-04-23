import pandas as pd
import pytest

from arpav_cline.thredds import ncss


@pytest.mark.parametrize(
    "raw_data, expected",
    [
        pytest.param(
            (
                'time,station,latitude[unit="degrees_north"],longitude[unit="degrees_east"],fake[unit="°C"]\n'
                "2020-01-25T00:00:00Z,GridPointRequestedAt[46.141N_12.809E],46.141,12.807,NaN\n"
            ),
            None,
        ),
        pytest.param(
            (
                'time,station,latitude[unit="degrees_north"],longitude[unit="degrees_east"],fake[unit="°C"]\n'
                "2020-01-25T00:00:00Z,GridPointRequestedAt[46.141N_12.809E],46.141,12.807,1.2\n"
                "2020-02-25T00:00:00Z,GridPointRequestedAt[46.141N_12.809E],46.141,12.807,2.3\n"
                "2020-03-25T00:00:00Z,GridPointRequestedAt[46.141N_12.809E],46.141,12.807,-34\n"
            ),
            pd.Series(
                data=[1.2, 2.3, -34],
                index=pd.DatetimeIndex(
                    data=[
                        "2020-01-25T00:00:00Z",
                        "2020-02-25T00:00:00Z",
                        "2020-03-25T00:00:00Z",
                    ],
                    tz="UTC",
                ),
                name="parsed_fake",
            ),
        ),
    ],
)
def test_parse_ncss_dataset(raw_data, expected):
    parsed = ncss._parse_ncss_dataset(
        raw_data,
        "fake",
        time_start=None,
        time_end=None,
        target_series_name="parsed_fake",
    )
    if expected is None:
        assert parsed == expected
    else:
        assert expected.equals(parsed)
