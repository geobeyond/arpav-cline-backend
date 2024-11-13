import dataclasses
import datetime as dt
import logging
from typing import Optional

import httpx
import numpy as np
import shapely

from . import (
    config,
    exceptions,
)
from .schemas import coverages
from .thredds import (
    crawler,
    ncss,
)

logger = logging.getLogger(__name__)


async def retrieve_coverage_data(
    settings: config.ArpavPpcvSettings,
    http_client: httpx.AsyncClient,
    cache_key: str,
    coverage: coverages.CoverageInternal,
    bbox: shapely.Polygon | None,
    temporal_range: tuple[Optional[dt.datetime], Optional[dt.datetime]],
):
    if (
        cache_path := settings.coverage_download_settings.cache_dir / cache_key
    ).is_file():
        logger.debug(f"Found cached data at {cache_path!r}...")
    else:
        logger.debug("Retrieving data from THREDDS server...")
        ds_fragment = crawler.get_thredds_url_fragment(
            coverage, settings.thredds_server.base_url
        )
        ncss_url = "/".join(
            (
                settings.thredds_server.base_url,
                settings.thredds_server.netcdf_subset_service_url_fragment,
                ds_fragment,
            )
        )
        logger.debug(f"{ncss_url=}")
        return await ncss.async_query_dataset_area(
            http_client,
            ncss_url,
            bbox=bbox,
            temporal_range=temporal_range,
        )


def get_cache_key(
    coverage: coverages.CoverageInternal,
    bbox: Optional[shapely.Polygon],
    temporal_range: tuple[Optional[dt.datetime], Optional[dt.datetime]],
) -> str:
    if bbox is not None:
        bbox_fragment = "-".join(f"{int(v * 10e4)}" for v in bbox.bounds)
    else:
        bbox_fragment = "full_extent"
    temporal_range_fragment = "-".join(
        t.strftime("%Y%m%d") if t is not None else "open" for t in temporal_range
    )
    result = f"{coverage.configuration.name}/"
    result += "___".join((coverage.identifier, bbox_fragment, temporal_range_fragment))
    result += ".nc"
    return result


@dataclasses.dataclass
class CoverageDownloadGrid:
    xx: np.array
    yy: np.array

    @property
    def shapely_box(self) -> shapely.Polygon:
        return shapely.box(
            xmin=self.xx[0],
            ymin=self.yy[0],
            xmax=self.xx[-1],
            ymax=self.yy[-1],
        )

    @property
    def shapely_multipoint(self) -> shapely.MultiPoint:
        pts = []
        for x in np.nditer(self.xx):
            for y in np.nditer(self.yy):
                pts.append(shapely.Point(x, y))
        return shapely.MultiPoint(pts)

    @property
    def shapely_multipolygon(self) -> shapely.MultiPolygon:
        pols = []
        for col in range(self.xx.size - 1):
            for row in range(self.yy.size - 1):
                pol = shapely.box(
                    xmin=self.xx[col],
                    xmax=self.xx[col + 1],
                    ymin=self.yy[row],
                    ymax=self.yy[row + 1],
                )
                pols.append(pol)
        return shapely.MultiPolygon(pols)

    @classmethod
    def from_config(cls, grid_conf: config.CoverageDownloadSpatialGrid):
        return cls(
            xx=np.linspace(
                start=float(grid_conf.min_lon),
                stop=float(grid_conf.max_lon),
                num=grid_conf.num_rows + 1,
            ),
            yy=np.linspace(
                start=float(grid_conf.min_lat),
                stop=float(grid_conf.max_lat),
                num=grid_conf.num_cols + 1,
            ),
        )

    def fit_bbox(self, bbox: shapely.Polygon) -> shapely.Polygon:
        min_x, min_y, max_x, max_y = bbox.bounds
        grid_min_x = self.xx[0]
        grid_max_x = self.xx[-1]
        grid_min_y = self.yy[0]
        grid_max_y = self.yy[-1]
        if self.shapely_box.intersects(bbox):
            min_x = max(min_x, grid_min_x)
            max_x = min(max_x, grid_max_x)
            min_y = max(min_y, grid_min_y)
            max_y = min(max_y, grid_max_y)
            snapped_min_x = np.max(self.xx[self.xx - min_x <= 0])
            snapped_min_y = np.max(self.yy[self.yy - min_y <= 0])
            snapped_max_x = np.min(self.xx[self.xx - max_x >= 0])
            snapped_max_y = np.min(self.yy[self.yy - max_y >= 0])
            return shapely.box(
                snapped_min_x, snapped_min_y, snapped_max_x, snapped_max_y
            )
        else:
            raise exceptions.CoverageDataRetrievalError("bbox does not intersect grid")
