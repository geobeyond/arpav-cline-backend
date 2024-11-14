import logging
import urllib.parse
from operator import itemgetter
from xml.etree import ElementTree as et
from typing import (
    Annotated,
    Optional,
    Sequence,
)

import anyio.to_thread
import httpx
import pydantic
import shapely.io
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from starlette.background import BackgroundTask

from .... import (
    database as db,
    datadownloads,
    exceptions,
    operations,
    palette,
)
from ....config import ArpavPpcvSettings
from ....thredds import (
    crawler as thredds_crawler,
    utils as thredds_utils,
)
from ....schemas.base import (
    CoverageDataSmoothingStrategy,
    ObservationDataSmoothingStrategy,
)
from ....schemas.coverages import ConfigurationParameterValue
from ....schemas.climaticindicators import ClimaticIndicator
from ... import dependencies
from ..schemas import coverages as coverage_schemas
from ..schemas.base import (
    TimeSeries,
    TimeSeriesList,
)


logger = logging.getLogger(__name__)
router = APIRouter()

_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL = "Invalid coverage identifier"


@router.get(
    "/configuration-parameters",
    response_model=coverage_schemas.ConfigurationParameterList,
)
def list_configuration_parameters(
    request: Request,
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    list_params: Annotated[dependencies.CommonListFilterParameters, Depends()],
    name_contains: str | None = None,
):
    """List configuration parameters."""
    config_params, filtered_total = db.list_configuration_parameters(
        db_session,
        limit=list_params.limit,
        offset=list_params.offset,
        include_total=True,
        name_filter=name_contains,
    )
    _, unfiltered_total = db.list_configuration_parameters(
        db_session, limit=1, offset=0, include_total=True
    )
    return coverage_schemas.ConfigurationParameterList.from_items(
        config_params,
        request,
        limit=list_params.limit,
        offset=list_params.offset,
        filtered_total=filtered_total,
        unfiltered_total=unfiltered_total,
    )


@router.get(
    "/coverage-configurations",
    response_model=coverage_schemas.CoverageConfigurationList,
)
def list_coverage_configurations(
    request: Request,
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    list_params: Annotated[dependencies.CommonListFilterParameters, Depends()],
    possible_value: Annotated[
        list[
            Annotated[
                str,
                pydantic.StringConstraints(pattern=r"^[0-9a-zA-Z_]+:[0-9a-zA-Z_]+$"),
            ]
        ],
        Query(),
    ] = None,
):
    """### List coverage configurations.

    A coverage configuration represents a set of multiple NetCDF files that are
    available in the ARPAV THREDDS server.

    A coverage configuration can be used to generate *coverage identifiers* that
    refer to individual NetCDF files by constructing a string based on the
    `dataset_id_pattern` property. For example, If there is a coverage configuration
    with the following properties:

    ```yaml
    name: myds
    coverage_id_pattern: {name}-something-{scenario}-{year_period}
    possible_values:
      - configuration_parameter_name: scenario
        configuration_parameter_value: scen1
      - configuration_parameter_name: scenario
        configuration_parameter_value: scen2
      - configuration_parameter_name: year_period
        configuration_parameter_value: winter
      - configuration_parameter_name: year_period
        configuration_parameter_value: autumn
    ```

    Then the following would be valid coverage identifiers:

    - `myds-something-scen1-winter`
    - `myds-something-scen1-autumn`
    - `myds-something-scen2-winter`
    - `myds-something-scen2-autumn`

    Each of these coverage identifiers could further be used to gain access to the WMS
    endpoint.

    """
    conf_param_values_filter, climatic_indicator = _retrieve_climatic_indicator_filter(
        db_session, possible_value or []
    )
    coverage_configurations, filtered_total = db.list_coverage_configurations(
        db_session,
        limit=list_params.limit,
        offset=list_params.offset,
        include_total=True,
        configuration_parameter_values_filter=conf_param_values_filter,
        climatic_indicator_filter=climatic_indicator,
    )
    _, unfiltered_total = db.list_coverage_configurations(
        db_session, limit=1, offset=0, include_total=True
    )
    return coverage_schemas.CoverageConfigurationList.from_items(
        coverage_configurations,
        request,
        limit=list_params.limit,
        offset=list_params.offset,
        filtered_total=filtered_total,
        unfiltered_total=unfiltered_total,
    )


@router.get(
    "/coverage-configurations/{coverage_configuration_id}",
    response_model=coverage_schemas.CoverageConfigurationReadDetail,
)
def get_coverage_configuration(
    request: Request,
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    coverage_configuration_id: pydantic.UUID4,
):
    db_coverage_configuration = db.get_coverage_configuration(
        db_session, coverage_configuration_id
    )
    allowed_coverage_identifiers = db.generate_coverage_identifiers(
        coverage_configuration=db_coverage_configuration
    )
    palette_colors = palette.parse_palette(
        db_coverage_configuration.palette, settings.palettes_dir
    )
    applied_colors = []
    if palette_colors is not None:
        minimum = db_coverage_configuration.color_scale_min
        maximum = db_coverage_configuration.color_scale_max
        if abs(maximum - minimum) > 0.001:
            applied_colors = palette.apply_palette(
                palette_colors, minimum, maximum, num_stops=settings.palette_num_stops
            )
        else:
            logger.warning(
                f"Cannot calculate applied colors for coverage "
                f"configuration {db_coverage_configuration.name!r} - check the "
                f"colorscale min and max values"
            )
    else:
        logger.warning(f"Unable to parse palette {db_coverage_configuration.palette!r}")
    return coverage_schemas.CoverageConfigurationReadDetail.from_db_instance(
        db_coverage_configuration, allowed_coverage_identifiers, applied_colors, request
    )


# PossibleValue: pydantic.StringConstraints(pattern="^[\w-_]+:[\w-_]+$")


@router.get(
    "/coverage-identifiers",
    response_model=coverage_schemas.CoverageIdentifierList,
)
def list_coverage_identifiers(
    request: Request,
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    list_params: Annotated[dependencies.CommonListFilterParameters, Depends()],
    name_contains: Annotated[list[str], Query()] = None,
    possible_value: Annotated[
        list[
            Annotated[
                str,
                pydantic.StringConstraints(pattern=r"^[0-9a-zA-Z_]+:[0-9a-zA-Z_]+$"),
            ]
        ],
        Query(),
    ] = None,
):
    conf_param_values_filter = []
    for possible in possible_value or []:
        param_name, param_value = possible.partition(":")[::2]
        db_parameter_value = db.get_configuration_parameter_value_by_names(
            db_session, param_name, param_value
        )
        if db_parameter_value is not None:
            conf_param_values_filter.append(db_parameter_value)
        else:
            logger.debug(
                f"ignoring unknown parameter/value pair {param_name}:{param_value}"
            )
    cov_internals, filtered_total = db.list_coverage_identifiers(
        db_session,
        limit=list_params.limit,
        offset=list_params.offset,
        include_total=True,
        name_filter=name_contains,
        configuration_parameter_values_filter=conf_param_values_filter or None,
    )
    _, unfiltered_total = db.list_coverage_identifiers(
        db_session, limit=1, offset=0, include_total=True
    )

    return coverage_schemas.CoverageIdentifierList.from_items(
        cov_internals,
        request,
        limit=list_params.limit,
        offset=list_params.offset,
        filtered_total=filtered_total,
        unfiltered_total=unfiltered_total,
    )


@router.get(
    "/coverage-identifiers/{coverage_identifier}",
    response_model=coverage_schemas.CoverageIdentifierReadListItem,
)
def get_coverage_identifier(
    request: Request,
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    coverage_identifier: str,
):
    if (coverage := db.get_coverage(db_session, coverage_identifier)) is not None:
        return coverage_schemas.CoverageIdentifierReadListItem.from_db_instance(
            coverage, request
        )
    else:
        raise HTTPException(400, detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL)


@router.get("/wms/{coverage_identifier}")
async def wms_endpoint(
    request: Request,
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    http_client: Annotated[httpx.AsyncClient, Depends(dependencies.get_http_client)],
    coverage_identifier: str,
    version: str = "1.3.0",
):
    """### Serve coverage via OGC Web Map Service.

    Pass additional relevant WMS query parameters directly to this endpoint.
    """

    cov = await anyio.to_thread.run_sync(
        db.get_coverage, db_session, coverage_identifier
    )
    if cov is not None:
        ds_fragment = thredds_crawler.get_thredds_url_fragment(
            cov, settings.thredds_server.base_url
        )

        base_wms_url = "/".join(
            (
                settings.thredds_server.base_url,
                settings.thredds_server.wms_service_url_fragment,
                ds_fragment,
            )
        )
        parsed_url = urllib.parse.urlparse(base_wms_url)
        logger.info(f"{base_wms_url=}")
        query_params = {k.lower(): v for k, v in request.query_params.items()}
        logger.debug(f"original query params: {query_params=}")
        if query_params.get("request") in ("GetMap", "GetLegendGraphic"):
            query_params = thredds_utils.tweak_wms_get_map_request(
                query_params,
                ncwms_palette=cov.configuration.climatic_indicator.palette,
                ncwms_color_scale_range=(
                    cov.configuration.climatic_indicator.color_scale_min,
                    cov.configuration.climatic_indicator.color_scale_max,
                ),
                uncertainty_visualization_scale_range=(
                    settings.thredds_server.uncertainty_visualization_scale_range
                ),
            )
        logger.debug(f"{query_params=}")
        wms_url = parsed_url._replace(
            query=urllib.parse.urlencode(
                {
                    **query_params,
                    "service": "WMS",
                    "version": version,
                }
            )
        ).geturl()
        logger.info(f"{wms_url=}")
        try:
            wms_response = await thredds_utils.proxy_request(wms_url, http_client)
        except httpx.HTTPStatusError as err:
            logger.exception(
                msg=f"THREDDS server replied with an error: {err.response.text}"
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY, detail=err.response.text
            )
        except httpx.HTTPError as err:
            logger.exception(msg="THREDDS server replied with an error")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
            ) from err
        else:
            if query_params.get("request") == "GetCapabilities":
                response_content = _modify_capabilities_response(
                    wms_response.text, str(request.url).partition("?")[0]
                )
            else:
                response_content = wms_response.content
            response = Response(
                content=response_content,
                status_code=wms_response.status_code,
                headers=dict(wms_response.headers),
            )
        return response
    else:
        raise HTTPException(
            status_code=400, detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL
        )


@router.get("/forecast-data")
def list_forecast_data_download_links(
    request: Request,
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    list_params: Annotated[dependencies.CommonListFilterParameters, Depends()],
    climatological_variable: Annotated[list[str], Query()] = None,
    aggregation_period: Annotated[list[str], Query()] = None,
    climatological_model: Annotated[list[str], Query()] = None,
    scenario: Annotated[list[str], Query()] = None,
    measure: Annotated[list[str], Query()] = None,
    year_period: Annotated[list[str], Query()] = None,
    time_window: Annotated[list[str], Query()] = None,
) -> coverage_schemas.CoverageDownloadList:
    """Get download links forecast data"""
    coverage_identifiers = operations.list_coverage_identifiers_by_param_values(
        db_session,
        climatological_variable,
        aggregation_period,
        climatological_model,
        scenario,
        measure,
        year_period,
        time_window,
        limit=list_params.limit,
        offset=list_params.offset,
    )
    return coverage_schemas.CoverageDownloadList.from_items(
        coverage_identifiers=coverage_identifiers,
        request=request,
        limit=list_params.limit,
        offset=list_params.offset,
        total=len(coverage_identifiers),
    )


@router.get("/forecast-data/{coverage_identifier}")
async def get_forecast_data(
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    http_client: Annotated[httpx.AsyncClient, Depends(dependencies.get_http_client)],
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    coverage_identifier: str,
    coords: Annotated[str, Query(description="A Well-Known-Text Polygon")] = None,
    datetime: Optional[str] = "../..",
):
    if (coverage := db.get_coverage(db_session, coverage_identifier)) is not None:
        used_values = coverage.configuration.retrieve_configuration_parameters(
            coverage.identifier
        )
        if used_values.get("aggregation_period") == "30yr":
            # Strip datetime query param if the underlying coverage has the
            # 30yr aggregation period because the upstream THREDDS NCSS
            # response is somehow returning an error if these datasets are
            # requested with a temporal range, even if the underlying NetCDF
            # temporal range is whithin the requested range.
            temporal_range = (None, None)
        else:
            temporal_range = operations.parse_temporal_range(datetime)
        if coords is not None:
            # FIXME - deal with invalid WKT errors
            geom = shapely.io.from_wkt(coords)
            if geom.geom_type == "Polygon":
                grid = datadownloads.CoverageDownloadGrid.from_config(
                    settings.coverage_download_settings.spatial_grid
                )
                try:
                    fitted_bbox = grid.fit_bbox(geom)
                except exceptions.CoverageDataRetrievalError as exc:
                    raise HTTPException(
                        status_code=400, detail=f"Invalid coords - {exc}"
                    )
            else:
                raise HTTPException(
                    status_code=400, detail="Invalid coords - Must be a WKT Polygon"
                )
        else:
            fitted_bbox = None

        cache_key = datadownloads.get_cache_key(coverage, fitted_bbox, temporal_range)
        response_to_stream = await datadownloads.retrieve_coverage_data(
            settings, http_client, cache_key, coverage, fitted_bbox, temporal_range
        )
        filename = cache_key.rpartition("/")[-1]
        return StreamingResponse(
            response_to_stream.aiter_bytes(),
            status_code=response_to_stream.status_code,
            media_type="application/netcdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
            background=BackgroundTask(response_to_stream.aclose),
        )
    else:
        raise HTTPException(
            status_code=400, detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL
        )


def _modify_capabilities_response(
    raw_response_content: str,
    wms_public_url: str,
) -> bytes:
    ns = {
        "wms": "http://www.opengis.net/wms",
        "xlink": "http://www.w3.org/1999/xlink",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "edal": "http://reading-escience-centre.github.io/edal-java/wms",
    }
    et.register_namespace("", ns["wms"])
    for prefix, uri in {k: v for k, v in ns.items() if k != "wms"}.items():
        et.register_namespace(prefix, uri)
    root = et.fromstring(raw_response_content)
    service_el = root.findall(f"{{{ns['wms']}}}Service")[0]

    # Remove the OnlineResource element, since we do not expose other
    # internal THREDDS server URLs
    for online_resource_el in service_el.findall(f"{{{ns['wms']}}}OnlineResource"):
        service_el.remove(online_resource_el)
    request_el = root.findall(f"{{{ns['wms']}}}Capability/{{{ns['wms']}}}Request")[0]

    # modify URLs for GetCapabilities, GetMap and GetFeatureInfo methods
    get_caps_el = request_el.findall(f"{{{ns['wms']}}}GetCapabilities")[0]
    get_map_el = request_el.findall(f"{{{ns['wms']}}}GetMap")[0]
    get_feature_info_el = request_el.findall(f"{{{ns['wms']}}}GetFeatureInfo")[0]
    for parent_el in (get_caps_el, get_map_el, get_feature_info_el):
        resource_el = parent_el.findall(
            f"{{{ns['wms']}}}DCPType/"
            f"{{{ns['wms']}}}HTTP/"
            f"{{{ns['wms']}}}Get/"
            f"{{{ns['wms']}}}OnlineResource"
        )[0]
        resource_el.set(f"{{{ns['xlink']}}}href", wms_public_url)
    # for each relevant layer, modify LegendURL and Style abstract
    for layer_el in root.findall(f".//{{{ns['wms']}}}Layer"):
        for legend_online_resource_el in layer_el.findall(
            f"./"
            f"{{{ns['wms']}}}Style/"
            f"{{{ns['wms']}}}LegendURL/"
            f"{{{ns['wms']}}}OnlineResource"
        ):
            attribute_name = f"{{{ns['xlink']}}}href"
            private_url = legend_online_resource_el.get(attribute_name)
            url_query = private_url.partition("?")[-1]
            new_url = "?".join((wms_public_url, url_query))
            legend_online_resource_el.set(f"{{{ns['xlink']}}}href", new_url)
        for abstract_el in layer_el.findall(
            f"./" f"{{{ns['wms']}}}Style/" f"{{{ns['wms']}}}Abstract"
        ):
            old_url_start = abstract_el.text.find("http")
            old_url = abstract_el.text[old_url_start:]
            query = old_url.partition("?")[-1]
            new_url = "?".join((wms_public_url, query))
            abstract_el.text = abstract_el.text[:old_url_start] + new_url
    return et.tostring(
        root,
        encoding="utf-8",
    )


@router.get(
    "/time-series/climate-barometer",
    response_model=TimeSeriesList,
)
def get_climate_barometer_time_series(
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    data_smoothing: Annotated[list[CoverageDataSmoothingStrategy], Query()] = [
        CoverageDataSmoothingStrategy.NO_SMOOTHING
    ],
    include_uncertainty: bool = False,
):
    """Get climate barometer time series."""
    try:
        relevant_series = operations.get_climate_barometer_time_series(
            settings,
            db_session,
            smoothing_strategies=data_smoothing,
            include_uncertainty=include_uncertainty,
        )
    except exceptions.CoverageDataRetrievalError as err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not retrieve data",
        ) from err
    else:
        series = []
        for coverage_info, pd_series in relevant_series.items():
            cov, smoothing_strategy = coverage_info
            series.append(
                TimeSeries.from_coverage_series(pd_series, cov, smoothing_strategy)
            )
        return TimeSeriesList(series=series)


@router.get("/time-series/{coverage_identifier}", response_model=TimeSeriesList)
def get_time_series(
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    http_client: Annotated[httpx.AsyncClient, Depends(dependencies.get_http_client)],
    coverage_identifier: str,
    coords: str,
    datetime: Optional[str] = "../..",
    include_coverage_data: bool = True,
    include_observation_data: Annotated[
        bool,
        Query(
            description=(
                "Whether data from the nearest observation station (if any) "
                "should be included in the response."
            )
        ),
    ] = False,
    coverage_data_smoothing: Annotated[list[CoverageDataSmoothingStrategy], Query()] = [
        CoverageDataSmoothingStrategy.NO_SMOOTHING
    ],  # noqa
    observation_data_smoothing: Annotated[
        list[ObservationDataSmoothingStrategy], Query()
    ] = [ObservationDataSmoothingStrategy.NO_SMOOTHING],  # noqa
    include_coverage_uncertainty: bool = False,
    include_coverage_related_data: bool = False,
):
    """### Get forecast-related time series for a geographic location.

    Given that a `coverage_identifier` represents a dataset generated by running a
    forecast model, this endpoint will return a representation of the various temporal
    series of data related to this forecast.
    """
    if (coverage := db.get_coverage(db_session, coverage_identifier)) is not None:
        # TODO: catch errors with invalid geom
        geom = shapely.io.from_wkt(coords)
        if geom.geom_type == "MultiPoint":
            logger.warning(
                f"Expected coords parameter to be a WKT Point but "
                f"got {geom.geom_type!r} instead - Using the first point"
            )
            point_geom = geom.geoms[0]
        elif geom.geom_type == "Point":
            point_geom = geom
        else:
            logger.warning(
                f"Expected coords parameter to be a WKT Point but "
                f"got {geom.geom_type!r} instead - Using the centroid instead"
            )
            point_geom = geom.centroid
        try:
            (
                coverage_series,
                observations_series,
            ) = operations.get_coverage_time_series(
                settings,
                db_session,
                http_client,
                coverage,
                point_geom,
                datetime,
                coverage_data_smoothing,
                observation_data_smoothing,
                include_coverage_data,
                include_observation_data,
                include_coverage_uncertainty,
                include_coverage_related_data,
            )
        except exceptions.CoverageDataRetrievalError as err:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not retrieve data",
            ) from err
        else:
            series = []
            for coverage_info, pd_series in coverage_series.items():
                cov, smoothing_strategy = coverage_info
                series.append(
                    TimeSeries.from_coverage_series(pd_series, cov, smoothing_strategy)
                )
            if observations_series is not None:
                for observation_info, pd_series in observations_series.items():
                    station, variable, smoothing_strategy = observation_info
                    series.append(
                        TimeSeries.from_observation_series(
                            pd_series, station, variable, smoothing_strategy
                        )
                    )
            return TimeSeriesList(series=series)
    else:
        raise HTTPException(
            status_code=400, detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL
        )


@router.get(
    "/forecast-variable-combinations",
    response_model=coverage_schemas.ForecastVariableCombinationsList,
)
def get_forecast_variable_combinations(
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
):
    variable_combinations = operations.get_forecast_variable_parameters(db_session)
    var_combinations = []
    for climatic_indicator, param_combinations in variable_combinations.items():
        var_combinations.append(
            (
                climatic_indicator.sort_order,
                climatic_indicator.aggregation_period.get_sort_order(),
                climatic_indicator.measure_type.get_sort_order(),
                coverage_schemas.ForecastVariableCombinations.from_items(
                    climatic_indicator, param_combinations
                ),
            )
        )
    var_combinations.sort(key=itemgetter(0, 1, 2))
    var_combinations = [vc[3] for vc in var_combinations]
    return coverage_schemas.ForecastVariableCombinationsList(
        combinations=var_combinations,
        translations=coverage_schemas.ForecastMenuTranslations.from_items(
            variable_combinations
        ),
    )


def _retrieve_climatic_indicator_filter(
    session: Session, configuration_parameter_values: Sequence[str]
) -> tuple[Optional[list[ConfigurationParameterValue]], Optional[ClimaticIndicator]]:
    conf_param_values_filter = []
    climatic_indicator_parts = {}
    for possible in configuration_parameter_values:
        param_name, param_value = possible.partition(":")[::2]
        if param_name in ("climatological_variable", "measure", "aggregation_period"):
            climatic_indicator_parts[param_name] = param_value
        else:
            db_parameter_value = db.get_configuration_parameter_value_by_names(
                session, param_name, param_value
            )
            if db_parameter_value is not None:
                conf_param_values_filter.append(db_parameter_value)
            else:
                logger.debug(
                    f"ignoring unknown parameter/value pair {param_name}:{param_value}"
                )
    climatic_indicator_id = "-".join(
        (
            climatic_indicator_parts.get("climatological_variable", ""),
            climatic_indicator_parts.get("measure", ""),
            climatic_indicator_parts.get("aggregation_period", ""),
        )
    )
    try:
        climatic_indicator = db.get_climatic_indicator_by_identifier(
            session, climatic_indicator_id
        )
    except exceptions.InvalidClimaticIndicatorIdentifierError as err:
        logger.debug(str(err))
        climatic_indicator = None
    return conf_param_values_filter or None, climatic_indicator
