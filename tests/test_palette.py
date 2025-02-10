from pathlib import Path
from unittest import mock

import pytest

from arpav_ppcv import palette


@pytest.mark.parametrize(
    "palette_name, expected",
    [
        pytest.param(
            "fake-palette1", ["#fake-color-1", "#fake-color-2", "#fake-color-3"]
        ),
        pytest.param(
            "fake-palette1-inv", ["#fake-color-3", "#fake-color-2", "#fake-color-1"]
        ),
        pytest.param(
            "default/fake-palette1", ["#fake-color-1", "#fake-color-2", "#fake-color-3"]
        ),
        pytest.param(
            "uncert-stippled/fake-palette1",
            ["#fake-color-1", "#fake-color-2", "#fake-color-3"],
        ),
        pytest.param(
            "default/fake-palette1-inv",
            ["#fake-color-3", "#fake-color-2", "#fake-color-1"],
        ),
        pytest.param(
            "fake-palette2", ["#fake-color-4", "#fake-color-5", "#fake-color-6"]
        ),
        pytest.param(
            "fake-palette2-inv", ["#fake-color-6", "#fake-color-5", "#fake-color-4"]
        ),
        pytest.param("other", None),
        pytest.param("nonsense", None),
    ],
)
def test_parse_palette(palette_name: str, expected: list[str]):
    fake_palette1_contents = [
        "#fake-color-1",
        "#fake-color-2",
        "#fake-color-3",
    ]
    fake_palette2_contents = [
        "#fake-color-4",
        "#fake-color-5",
        "#fake-color-6",
        "this is not a color",
        "%this is also not a color",
    ]
    fake_other_contents = [
        "something-else",
    ]
    fake_palette1 = mock.MagicMock(spec=Path)
    fake_palette1.configure_mock(
        **{
            "stem": "fake-palette1",
            "read_text.return_value": "\n".join(fake_palette1_contents),
            "is_file.return_value": True,
        }
    )
    fake_palette2 = mock.MagicMock(
        spec=Path,
        **{
            "stem": "fake-palette2",
            "read_text.return_value": "\n".join(fake_palette2_contents),
            "is_file.return_value": True,
        },
    )
    fake_other = mock.MagicMock(
        spec=Path,
        **{
            "stem": "other",
            "read_text.return_value": "\n".join(fake_other_contents),
            "is_file.return_value": True,
        },
    )
    mock_palettes_dir = mock.MagicMock(spec=Path)
    mock_palettes_dir.iterdir.return_value = [
        fake_palette1,
        fake_palette2,
        fake_other,
    ]
    result = palette.parse_palette(palette_name, mock_palettes_dir)
    assert result == expected


@pytest.mark.parametrize(
    "colors, minimum, maximum, expected",
    [
        pytest.param(
            [
                "#FF003c30",
                "#FF01665e",
                "#FF35978f",
                "#FF80cdc1",
                "#FFc7eae5",
                "#FFf5f5f5",
                "#FFf6e8c3",
                "#FFdfc27d",
                "#FFbf812d",
                "#FF8c510a",
                "#FF543005",
            ],
            -40,
            40,
            [
                (-40.0, "#ff003c30"),
                (-20.0, "#ff5ab1a7"),
                (0.0, "#fff5f5f4"),
                (20.0, "#ffcfa154"),
                (40.0, "#ff543005"),
            ],
        ),
    ],
)
def test_apply_palette(
    colors: list[str], minimum: float, maximum: float, expected: list[tuple[float, str]]
):
    result = palette.apply_palette(colors, minimum, maximum, num_stops=5)
    assert result == expected
