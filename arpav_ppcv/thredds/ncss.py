"""Utilities for interacting with the THREDDS NetCDF Subset Service (NCSS).

Get more detail about NCSS at:

https://docs.unidata.ucar.edu/tds/current/userguide/netcdf_subset_service_ref.html

"""
import datetime as dt
import logging
import xml.etree.ElementTree as etree

import httpx
import shapely

from ..exceptions import CoverageDataRetrievalError
from . import models

logger = logging.getLogger(__name__)


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
