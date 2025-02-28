import logging

import httpx

from . import models
from ..schemas.base import CoreConfParamName

logger = logging.getLogger(__name__)


def build_dataset_service_url(
    dataset_configuration_id: str,
    pattern_fields: dict[str, str],
    *,
    url_path_pattern: str,
    thredds_base_url: str,
    service_url_fragment: str,
) -> str:
    rendered = url_path_pattern.format(
        **{"configuration_id": dataset_configuration_id, **pattern_fields}
    )
    return "/".join((thredds_base_url, service_url_fragment, rendered))


def get_parameter_internal_value(name: str, value: str) -> str:
    if name == CoreConfParamName.SCENARIO.value:
        parsed_value = models.ForecastScenario[value.upper()].value.code
    elif name == CoreConfParamName.YEAR_PERIOD.value:
        parsed_value = models.ForecastYearPeriod[value.upper()].value.code
    else:
        parsed_value = value
    return parsed_value


async def proxy_request(url: str, http_client: httpx.AsyncClient) -> httpx.Response:
    response = await http_client.get(url)
    response.raise_for_status()
    return response


def tweak_wms_get_map_request(
    query_params: dict[str, str],
    ncwms_palette: str,
    ncwms_color_scale_range: tuple[float, float],
    uncertainty_visualization_scale_range: tuple[float, float],
) -> dict[str, str]:
    # which layer type is being requested?

    # - WMS GetMap allows requesting multiple layers, therefore the query param is
    #   called `layers`
    # - WMS GetLegendGraphic works for individual layers, therefore the query param is
    #   called `layer`
    layer_name = query_params.get("layers", query_params.get("layer", ""))

    if "agree" in layer_name:
        palette = "default/seq-Greys"
        color_scale_range = "0,1"
        num_color_bands = "2"
        query_params["NUMCOLORBANDS"] = num_color_bands
    else:
        num_color_bands = "250"
        if "uncertainty_group" in layer_name:
            palette = ncwms_palette
        else:
            palette = f"default/{ncwms_palette.rpartition('/')[-1]}"

        if not (requested_color_scale_range := query_params.get("colorscalerange")):
            color_scale_range = ",".join(str(f) for f in ncwms_color_scale_range)
            if "stippled" in palette:
                uncert_scale_range = ",".join(
                    str(f) for f in uncertainty_visualization_scale_range
                )
                color_scale_range = ";".join((color_scale_range, uncert_scale_range))
        else:
            color_scale_range = requested_color_scale_range

    query_params["styles"] = palette
    query_params["colorscalerange"] = color_scale_range
    query_params["NUMCOLORBANDS"] = num_color_bands
    query_params["ABOVEMAXCOLOR"] = "extend"
    query_params["BELOWMINCOLOR"] = "extend"
    return query_params
