import logging
from pathlib import Path
from typing import (
    Optional,
    Sequence,
)

import matplotlib as mpl

logger = logging.getLogger(__name__)


def apply_palette(
    colors: Sequence[str], minimum: float, maximum: float, num_stops: int
) -> list[tuple[float, str]]:
    # this converts from the AARRGGBB format which is what the .pal files have
    # to RRGGBB
    rgb_colors = [f"#{c[3:]}" for c in colors]
    cmap = mpl.colors.LinearSegmentedColormap.from_list(
        "arpav-palette", rgb_colors, N=250
    )
    result = []
    step = (maximum - minimum) / (num_stops - 1)
    for current_stop in range(num_stops):
        interval_stop = minimum + current_stop * step
        normalized_stop = current_stop * step / abs(maximum - minimum)
        color = mpl.colors.to_hex(cmap(normalized_stop), True)
        thredds_representation = "#{alpha}{red}{green}{blue}".format(
            red=color[1:3],
            green=color[3:5],
            blue=color[5:7],
            alpha=color[7:9],
        )
        result.append((interval_stop, thredds_representation))
    return result


def parse_palette(palette: str, palettes_dir: Path) -> Optional[list[str]]:
    palette_name = palette.split("/")[-1].lower()
    if is_inverted := "-inv" in palette_name:
        name = palette_name.replace("-inv", "")
    else:
        name = palette_name
    colors = []
    for file_path in [f for f in palettes_dir.iterdir() if f.is_file()]:
        if file_path.stem.lower() == name:
            try:
                colors = [
                    line.strip()
                    for line in file_path.read_text().splitlines()
                    if line.startswith("#")
                ]
            except OSError:
                logger.warning(f"Error reading file {file_path}")
            break
    else:
        logger.warning(f"Could not find a palette named {name!r} at {palettes_dir!r}")
    if is_inverted:
        colors.reverse()
    return colors if len(colors) > 0 else None
