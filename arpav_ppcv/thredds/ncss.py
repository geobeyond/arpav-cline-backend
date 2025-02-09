"""Utilities for interacting with the THREDDS NetCDF Subset Service (NCSS).

Get more detail about NCSS at:

https://docs.unidata.ucar.edu/tds/current/userguide/netcdf_subset_service_ref.html

"""
import dataclasses
import datetime as dt
import io
import logging
import xml.etree.ElementTree as etree
from typing import (
    Optional,
    Protocol,
    Union,
    TYPE_CHECKING,
)

import httpx
import pandas as pd
import shapely
from pandas.core.indexes.datetimes import DatetimeIndex

from ..exceptions import CoverageDataRetrievalError
from . import models

if TYPE_CHECKING:
    from ..config import ThreddsServerSettings
    from ..schemas.coverages import (
        ForecastCoverageInternal,
    )

logger = logging.getLogger(__name__)


class RetrievableCoverageProtocol(Protocol):
    identifier: str

    def get_thredds_ncss_url(self, settings: "ThreddsServerSettings") -> Optional[str]:
        ...

    def get_netcdf_main_dataset_name(self) -> Optional[str]:
        ...


@dataclasses.dataclass
class SimpleCoverageDataRetriever:
    settings: "ThreddsServerSettings"
    http_client: httpx.Client
    coverage: RetrievableCoverageProtocol

    def retrieve_main_data(
        self,
        location: shapely.Point,
        temporal_range: Optional[tuple[dt.date | None, dt.date | None]] = None,
        target_series_name: Optional[str] = None,
    ) -> Optional[pd.Series]:
        ncss_url = self.coverage.get_thredds_ncss_url(self.settings)
        netcdf_variable_name = self.coverage.get_netcdf_main_dataset_name()
        if all((ncss_url, netcdf_variable_name)):
            return self._retrieve_location_data(
                ncss_url,
                netcdf_variable_name,
                location,
                temporal_range,
                target_series_name=target_series_name or self.coverage.identifier,
            )
        elif ncss_url is None:
            logger.warning("Could not find coverage's NCSS URL")
        else:
            logger.warning("Could not find coverage's NetCDF variable name")

    def _retrieve_location_data(
        self,
        ncss_url: str,
        netcdf_variable_name: str,
        location: shapely.Point,
        temporal_range: Optional[tuple[dt.date | None, dt.date | None]] = None,
        target_series_name: Optional[str] = None,
    ) -> Optional[pd.Series]:
        result = None
        raw_data = query_dataset(
            self.http_client,
            thredds_ncss_url=ncss_url,
            variable_name=netcdf_variable_name,
            longitude=location.x,
            latitude=location.y,
            time_start=temporal_range[0],
            time_end=temporal_range[1],
        )
        if raw_data is not None:
            result = _parse_ncss_dataset(
                raw_data,
                netcdf_variable_name,
                time_start=temporal_range[0] if temporal_range else None,
                time_end=temporal_range[1] if temporal_range else None,
                target_series_name=target_series_name,
            )
        else:
            logger.info(f"Did not receive any data from {ncss_url!r}")
        return result


@dataclasses.dataclass
class ForecastCoverageDataRetriever(SimpleCoverageDataRetriever):
    coverage: "ForecastCoverageInternal"

    def retrieve_main_data(
        self,
        location: shapely.Point,
        temporal_range: Optional[tuple[dt.date | None, dt.date | None]] = None,
        target_series_name: Optional[str] = None,
    ) -> Optional[pd.Series]:
        ncss_url = self.coverage.get_thredds_ncss_url(self.settings)
        netcdf_variable_name = self.coverage.get_netcdf_main_dataset_name()
        if all((ncss_url, netcdf_variable_name)):
            return self._retrieve_location_data(
                ncss_url,
                netcdf_variable_name,
                location,
                temporal_range,
                target_series_name=target_series_name or self.coverage.identifier,
            )
        elif ncss_url is None:
            logger.warning("Could not find coverage's NCSS URL")
        else:
            logger.warning("Could not find coverage's NetCDF variable name")

    def retrieve_lower_uncertainty_data(
        self,
        location: shapely.Point,
        temporal_range: Optional[tuple[dt.date | None, dt.date | None]] = None,
        target_series_name: Optional[str] = None,
    ) -> Optional[pd.Series]:
        identifier = target_series_name or self.coverage.lower_uncertainty_identifier
        ncss_url = self.coverage.get_lower_uncertainty_thredds_ncss_url(self.settings)
        netcdf_variable_name = (
            self.coverage.get_netcdf_lower_uncertainty_main_dataset_name()
        )
        result = None
        if all((identifier, ncss_url, netcdf_variable_name)):
            result = self._retrieve_location_data(
                ncss_url,
                netcdf_variable_name,
                location,
                temporal_range,
                target_series_name=identifier,
            )
        elif identifier is None:
            logger.info(
                f"Coverage {self.coverage.identifier!r} does not specify a lower "
                f"uncertainty dataset"
            )
        elif ncss_url is None:
            logger.warning("Could not find coverage's lower uncertainty NCSS URL")
        else:
            logger.warning("Could not find coverage's NetCDF variable name")
        return result

    def retrieve_upper_uncertainty_data(
        self,
        location: shapely.Point,
        temporal_range: Optional[tuple[dt.date | None, dt.date | None]] = None,
        target_series_name: Optional[str] = None,
    ) -> Optional[pd.Series]:
        identifier = target_series_name or self.coverage.upper_uncertainty_identifier
        ncss_url = self.coverage.get_upper_uncertainty_thredds_ncss_url(self.settings)
        netcdf_variable_name = (
            self.coverage.get_netcdf_upper_uncertainty_main_dataset_name()
        )
        logger.debug(f"{identifier=}")
        logger.debug(f"{ncss_url=}")
        logger.debug(f"{netcdf_variable_name=}")
        if all((identifier, ncss_url, netcdf_variable_name)):
            return self._retrieve_location_data(
                ncss_url,
                netcdf_variable_name,
                location,
                temporal_range,
                target_series_name=identifier,
            )
        elif identifier is None:
            logger.warning(
                f"Coverage {self.coverage.identifier!r} does not specify an upper "
                f"uncertainty dataset"
            )
        elif ncss_url is None:
            logger.warning("Could not find coverage's upper uncertainty NCSS URL")
        else:
            logger.warning("Could not find coverage's NetCDF variable name")


def _parse_ncss_dataset(
    raw_data: str,
    source_main_ds_name: str,
    time_start: dt.datetime | None,
    time_end: dt.datetime | None,
    target_series_name: str | None = None,
) -> pd.Series:
    df = pd.read_csv(io.StringIO(raw_data), parse_dates=["time"])
    try:
        col_name = [c for c in df.columns if c.startswith(f"{source_main_ds_name}[")][0]
    except IndexError:
        raise RuntimeError(
            f"Could not extract main data series from dataframe "
            f"with columns {df.columns}"
        )
    else:
        # keep only time and main variable - we don't care about other stuff
        df = df[["time", col_name]]
        if target_series_name is not None:
            df = df.rename(columns={col_name: target_series_name})

        # - filter out values outside the temporal range
        df.set_index("time", inplace=True)

        # check that we got a datetime index, otherwise we need to modify the values
        if type(df.index) is not DatetimeIndex:
            new_index = pd.to_datetime(df.index.map(_simplify_date))
            df.index = new_index

        if time_start is not None:
            df = df[time_start:]
        if time_end is not None:
            df = df[:time_end]
        return df.squeeze()


def _simplify_date(raw_date: str) -> str:
    """Simplify a date by loosing its day and time information.

    This will reset a date to the 15th day of the underlying month.
    """
    raw_year, raw_month = raw_date.split("-")[:2]
    return f"{raw_year}-{raw_month}-15T00:00:00+00:00"


async def async_get_dataset_description(
    http_client: httpx.AsyncClient,
    thredds_ncss_url: str,
) -> models.ThreddsDatasetDescription:
    response = await http_client.get(f"{thredds_ncss_url}/dataset.xml")
    response.raise_for_status()
    root = etree.fromstring(response.text)
    variables = []
    for var_info in root.findall("./gridSet/grid"):
        variables.append(
            models.ThreddsDatasetDescriptionVariable(
                name=var_info.get("name"),
                description=var_info.get("desc"),
                units=var_info.findall("./*[@name='units']")[0].get("value"),
            )
        )
    time_span_el = root.findall("./TimeSpan")[0]
    temporal_bounds = models.ThreddsDatasetDescriptionTemporalBounds(
        start=dt.datetime.fromisoformat(
            time_span_el.findall("./begin")[0].text.replace("Z", "")
        ),
        end=dt.datetime.fromisoformat(
            time_span_el.findall("./end")[0].text.replace("Z", "")
        ),
    )
    lat_lon_el = root.findall("./LatLonBox")[0]
    spatial_bounds = shapely.box(
        xmin=float(lat_lon_el.findall("./west")[0].text),
        ymin=float(lat_lon_el.findall("./south")[0].text),
        xmax=float(lat_lon_el.findall("./east")[0].text),
        ymax=float(lat_lon_el.findall("./north")[0].text),
    )
    return models.ThreddsDatasetDescription(
        variables=variables,
        spatial_bounds=spatial_bounds,
        temporal_bounds=temporal_bounds,
    )


def get_dataset_description(
    http_client: httpx.Client,
    thredds_ncss_url: str,
) -> models.ThreddsDatasetDescription:
    response = http_client.get(f"{thredds_ncss_url}/dataset.xml")
    response.raise_for_status()
    root = etree.fromstring(response.text)
    variables = []
    for var_info in root.findall("./gridSet/grid"):
        variables.append(
            models.ThreddsDatasetDescriptionVariable(
                name=var_info.get("name"),
                description=var_info.get("desc"),
                units=var_info.findall("./*[@name='units']")[0].get("value"),
            )
        )
    time_span_el = root.findall("./TimeSpan")[0]
    temporal_bounds = models.ThreddsDatasetDescriptionTemporalBounds(
        start=dt.datetime.fromisoformat(time_span_el.findall("./begin")[0].text),
        end=dt.datetime.fromisoformat(time_span_el.findall("./end")[0].text),
    )
    lat_lon_el = root.findall("./LatLonBox")[0]
    spatial_bounds = shapely.box(
        xmin=float(lat_lon_el.findall("./west")[0].text),
        ymin=float(lat_lon_el.findall("./south")[0].text),
        xmax=float(lat_lon_el.findall("./east")[0].text),
        ymax=float(lat_lon_el.findall("./north")[0].text),
    )
    return models.ThreddsDatasetDescription(
        variables=variables,
        spatial_bounds=spatial_bounds,
        temporal_bounds=temporal_bounds,
    )


async def async_query_dataset_area(
    http_client: httpx.AsyncClient,
    thredds_ncss_url: str,
    netcdf_variable_names: list[str] | None = None,
    bbox: shapely.Polygon | None = None,
    temporal_range: tuple[dt.datetime | None, dt.datetime | None] | None = None,
):
    """Query THREDDS for the specified variables, spatial and temporal extents."""
    time_start = temporal_range[0]
    time_end = temporal_range[1]
    need_info = (
        len(netcdf_vars := netcdf_variable_names or []) == 0
        or (time_start is None and time_end is not None)
        or (time_end is None and time_start is not None)
    )
    if need_info:
        info = await async_get_dataset_description(http_client, thredds_ncss_url)
        netcdf_vars = (
            [v.name for v in info.variables] if len(netcdf_vars) == 0 else netcdf_vars
        )
        time_start = info.temporal_bounds.start if time_start is None else time_start
        time_end = info.temporal_bounds.end if time_end is None else time_end

    temporal_parameters = {}
    if time_start is None and time_end is None:
        temporal_parameters["time"] = "all"
    else:
        temporal_parameters.update(
            {
                "time_start": time_start.isoformat(),
                "time_end": time_end.isoformat(),
            }
        )
    spatial_parameters = {}
    if bbox is not None:
        min_x, min_y, max_x, max_y = bbox.bounds
        spatial_parameters.update(
            {
                "north": max_y,
                "south": min_y,
                "east": max_x,
                "west": min_x,
            }
        )
    ncss_params = {
        "accept": "netCDF4",
        "var": ",".join(netcdf_vars),
        **temporal_parameters,
        **spatial_parameters,
    }
    request = http_client.build_request("GET", thredds_ncss_url, params=ncss_params)
    return await http_client.send(request, stream=True)


async def async_query_dataset(
    http_client: httpx.AsyncClient,
    thredds_ncss_url: str,
    netcdf_variable_name: str,
    longitude: float,
    latitude: float,
    time_start: dt.datetime | None = None,
    time_end: dt.datetime | None = None,
):
    """Query THREDDS for the specified variable."""
    if time_start is None or time_end is None:
        temporal_parameters = {
            "time": "all",
        }
    else:
        temporal_parameters = {
            "time_start": time_start.isoformat(),
            "time_end": time_end.isoformat(),
        }
    response = await http_client.get(
        thredds_ncss_url,
        params={
            "var": netcdf_variable_name,
            "latitude": latitude,
            "longitude": longitude,
            "accept": "CSV",
            **temporal_parameters,
        },
    )
    try:
        response.raise_for_status()
    except httpx.HTTPError as err:
        logger.exception(msg="Could not retrieve data")
        logger.debug(f"upstream NCSS error: {response.content}")
        raise CoverageDataRetrievalError() from err
    else:
        result = response.text
    return result


def query_dataset(
    http_client: httpx.Client,
    thredds_ncss_url: str,
    variable_name: str,
    longitude: float,
    latitude: float,
    time_start: dt.datetime | None = None,
    time_end: dt.datetime | None = None,
) -> str:
    """Query THREDDS for the specified variable."""
    if time_start is None or time_end is None:
        temporal_parameters = {
            "time": "all",
        }
    else:
        temporal_parameters = {
            "time_start": time_start.isoformat(),
            "time_end": time_end.isoformat(),
        }
    response = http_client.get(
        thredds_ncss_url,
        params={
            "var": variable_name,
            "latitude": latitude,
            "longitude": longitude,
            "accept": "CSV",
            **temporal_parameters,
        },
    )
    try:
        response.raise_for_status()
    except httpx.HTTPError as err:
        logger.exception(msg="Could not retrieve data")
        logger.debug(f"upstream NCSS error: {response.content}")
        raise CoverageDataRetrievalError() from err
    else:
        result = response.text
    return result
