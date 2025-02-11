import logging
import urllib.parse
from xml.etree import ElementTree as et
from typing import (
    Annotated,
    Optional,
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
    db,
    datadownloads,
    exceptions,
    operations,
    palette,
    timeseries,
)
from ....config import ArpavPpcvSettings
from ....thredds import utils as thredds_utils
from ....schemas.legacy import (
    CoverageDataSmoothingStrategy,
)
from ....schemas.static import (
    AggregationPeriod,
    CoverageTimeSeriesProcessingMethod,
    ObservationTimeSeriesProcessingMethod,
    DataCategory,
)
from ... import dependencies
from ..schemas import coverages as coverage_schemas
from ..schemas.timeseries import (
    LegacyTimeSeries,
    LegacyTimeSeriesList,
    TimeSeries,
    TimeSeriesList,
)
from ...frontendutils.schemas import (
    LegacyForecastVariableCombinationsList,
    LegacyForecastVariableCombinations,
    LegacyForecastMenuTranslations,
)
from ...frontendutils.navigation import get_forecast_advanced_section_navigation


logger = logging.getLogger(__name__)
router = APIRouter()

_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL = "Invalid coverage identifier"


@router.get(
    "/configuration-parameters",
    response_model=coverage_schemas.LegacyConfigurationParameterList,
)
def list_legacy_configuration_parameters(
    request: Request,
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    list_params: Annotated[dependencies.CommonListFilterParameters, Depends()],
    name_contains: str | None = None,
):
    """List coverage-related configuration parameters.

    Lists configuration parameters which can be used when filtering for coverages.
    """
    config_params, filtered_total = db.legacy_list_configuration_parameters(
        db_session,
        limit=list_params.limit,
        offset=list_params.offset,
        include_total=True,
        name_filter=name_contains,
    )
    _, unfiltered_total = db.legacy.legacy_list_configuration_parameters(
        db_session, limit=1, offset=0, include_total=True
    )
    return coverage_schemas.LegacyConfigurationParameterList.from_items(
        config_params,
        request,
        limit=list_params.limit,
        offset=list_params.offset,
        filtered_total=filtered_total,
        unfiltered_total=unfiltered_total,
    )


@router.get(
    "/coverage-configurations",
    response_model=coverage_schemas.LegacyCoverageConfigurationList,
)
def list_coverage_configurations(
    request: Request,
    session: Annotated[Session, Depends(dependencies.get_db_session)],
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
    """List existing coverage configurations."""
    filter_values = operations.convert_conf_params_filter(session, possible_value or [])
    logger.debug(f"{filter_values=}")
    include_forecasts = False
    include_historical = False
    if filter_values.archive is not None:
        if filter_values.archive == DataCategory.FORECAST.value:
            include_forecasts = True
        elif filter_values.archive == DataCategory.HISTORICAL.value:
            include_historical = True
        else:
            raise exceptions.InvalidArchiveError()
    else:
        include_forecasts = True
        include_historical = True

    filtered_forecast_cov_confs = []
    filtered_historical_cov_confs = []
    unfiltered_forecast_cov_confs = []
    unfiltered_historical_cov_confs = []
    if include_forecasts:
        filtered_forecast_cov_confs = (
            db.legacy_collect_all_forecast_coverage_configurations(
                session, conf_param_filter=filter_values
            )
        )
        unfiltered_forecast_cov_confs = (
            db.legacy_collect_all_forecast_coverage_configurations(session)
        )
    if include_historical:
        filtered_historical_cov_confs = (
            db.legacy_collect_all_historical_coverage_configurations(
                session, conf_param_filter=filter_values
            )
        )
        unfiltered_historical_cov_confs = (
            db.legacy_collect_all_historical_coverage_configurations(session)
        )

    return coverage_schemas.LegacyCoverageConfigurationList.from_items(
        filtered_forecast_cov_confs,
        filtered_historical_cov_confs,
        request,
        limit=list_params.limit,
        offset=list_params.offset,
        unfiltered_total_forecast_coverage_configurations=len(
            unfiltered_forecast_cov_confs
        ),
        unfiltered_total_historical_coverage_configurations=len(
            unfiltered_historical_cov_confs
        ),
    )


@router.get(
    "/forecast-coverage-configurations/{forecast_coverage_configuration_identifier}",
    response_model=coverage_schemas.LegacyForecastCoverageConfigurationReadDetail,
)
def get_forecast_coverage_configuration(
    request: Request,
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    forecast_coverage_configuration_identifier: str,
):
    cov_conf = db.get_forecast_coverage_configuration_by_identifier(
        db_session, forecast_coverage_configuration_identifier
    )
    coverages = db.generate_forecast_coverages_from_configuration(cov_conf)

    palette_colors = palette.parse_palette(
        cov_conf.climatic_indicator.palette, settings.palettes_dir
    )
    applied_colors = []
    if palette_colors is not None:
        minimum = cov_conf.climatic_indicator.color_scale_min
        maximum = cov_conf.climatic_indicator.color_scale_max
        if abs(maximum - minimum) > 0.001:
            applied_colors = palette.apply_palette(
                palette_colors, minimum, maximum, num_stops=settings.palette_num_stops
            )
        else:
            logger.warning(
                f"Cannot calculate applied colors for coverage "
                f"configuration {cov_conf.identifier!r} - "
                f"check the respective climatic indicator's colorscale min "
                f"and max values"
            )
    else:
        logger.warning(
            f"Unable to parse palette " f"{cov_conf.climatic_indicator.palette!r}"
        )
    return (
        coverage_schemas.LegacyForecastCoverageConfigurationReadDetail.from_db_instance(
            cov_conf,
            coverages,
            applied_colors,
            request,
        )
    )


@router.get(
    "/historical-coverage-configurations/{historical_coverage_configuration_identifier}",
    response_model=coverage_schemas.LegacyHistoricalCoverageConfigurationReadDetail,
)
def get_historical_coverage_configuration(
    request: Request,
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    historical_coverage_configuration_identifier: str,
):
    cov_conf = db.get_historical_coverage_configuration_by_identifier(
        db_session, historical_coverage_configuration_identifier
    )
    coverages = db.generate_historical_coverages_from_configuration(cov_conf)

    palette_colors = palette.parse_palette(
        cov_conf.climatic_indicator.palette, settings.palettes_dir
    )
    applied_colors = []
    if palette_colors is not None:
        minimum = cov_conf.climatic_indicator.color_scale_min
        maximum = cov_conf.climatic_indicator.color_scale_max
        if abs(maximum - minimum) > 0.001:
            applied_colors = palette.apply_palette(
                palette_colors, minimum, maximum, num_stops=settings.palette_num_stops
            )
        else:
            logger.warning(
                f"Cannot calculate applied colors for coverage "
                f"configuration {cov_conf.identifier!r} - "
                f"check the respective climatic indicator's colorscale min "
                f"and max values"
            )
    else:
        logger.warning(
            f"Unable to parse palette " f"{cov_conf.climatic_indicator.palette!r}"
        )
    return coverage_schemas.LegacyHistoricalCoverageConfigurationReadDetail.from_db_instance(
        cov_conf,
        coverages,
        applied_colors,
        request,
    )


@router.get(
    "/coverage-identifiers",
    response_model=coverage_schemas.LegacyForecastCoverageList,
)
def legacy_list_forecast_coverage_identifiers(
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
    conf_param_filter = operations.convert_conf_params_filter(
        db_session, possible_value or []
    )
    logger.debug(f"{conf_param_filter=}")
    cov_internals, filtered_total = db.legacy_list_forecast_coverages(
        db_session,
        limit=list_params.limit,
        offset=list_params.offset,
        include_total=True,
        name_filter=name_contains,
        conf_param_filter=conf_param_filter,
    )
    _, unfiltered_total = db.legacy_list_forecast_coverages(
        db_session, limit=1, offset=0, include_total=True
    )
    return coverage_schemas.LegacyForecastCoverageList.from_items(
        cov_internals,
        request,
        limit=list_params.limit,
        offset=list_params.offset,
        filtered_total=filtered_total,
        unfiltered_total=unfiltered_total,
    )


@router.get(
    "/historical-coverages/{coverage_identifier}",
    response_model=coverage_schemas.LegacyHistoricalCoverageReadDetail,
)
def get_historical_coverage(
    request: Request,
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    coverage_identifier: str,
):
    coverage = db.get_historical_coverage(db_session, coverage_identifier)
    if coverage is not None:
        return coverage_schemas.LegacyHistoricalCoverageReadDetail.from_db_instance(
            coverage, request
        )
    else:
        raise HTTPException(400, detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL)


@router.get(
    "/forecast-coverages/{coverage_identifier}",
    response_model=coverage_schemas.LegacyForecastCoverageReadDetail,
)
def get_forecast_coverage(
    request: Request,
    session: Annotated[Session, Depends(dependencies.get_db_session)],
    coverage_identifier: str,
):
    coverage = db.get_forecast_coverage(session, coverage_identifier)
    if coverage is not None:
        return coverage_schemas.LegacyForecastCoverageReadDetail.from_db_instance(
            coverage, request
        )
    else:
        raise HTTPException(400, detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL)


@router.get(
    "/coverage-identifiers/{coverage_identifier}",
    response_model=coverage_schemas.LegacyForecastCoverageReadDetail,
    deprecated=True,
)
def get_coverage_identifier(
    request: Request,
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    coverage_identifier: str,
):
    """Returns forecast coverages

    Use /forecast-coverages/{coverage_identifier} instead
    """
    return get_forecast_coverage(request, db_session, coverage_identifier)


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

    if coverage_identifier.split("-")[0] == "forecast":
        cov = await anyio.to_thread.run_sync(
            db.get_forecast_coverage,
            db_session,
            coverage_identifier,
        )
    else:
        cov = None

    if cov is not None:
        base_wms_url = cov.get_wms_base_url(settings.thredds_server)
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
    if (
        coverage := db.get_forecast_coverage(db_session, coverage_identifier)
    ) is not None:
        if (
            coverage.configuration.climatic_indicator.aggregation_period
            == AggregationPeriod.THIRTY_YEAR.value
        ):
            # Strip datetime query param if the underlying coverage has the
            # 30yr aggregation period because the upstream THREDDS NCSS
            # response is somehow returning an error if these datasets are
            # requested with a temporal range, even if the underlying NetCDF
            # temporal range is within the requested range.
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
def get_overview_time_series(
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    data_smoothing: Annotated[list[CoverageDataSmoothingStrategy], Query()] = [
        CoverageDataSmoothingStrategy.NO_SMOOTHING
    ],
    include_uncertainty: bool = False,
):
    """Get climate barometer time series."""
    # converting from legacy data_smoothing enum
    processing_methods = [
        strategy.to_processing_method() for strategy in data_smoothing
    ]
    try:
        (
            forecast_overview_time_series,
            observation_overview_time_series,
        ) = timeseries.get_overview_time_series(
            settings=settings,
            session=db_session,
            processing_methods=processing_methods,
            include_uncertainty=include_uncertainty,
        )
    except exceptions.OverviewDataRetrievalError as err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not retrieve data",
        ) from err
    else:
        series = []
        for forecast_series in forecast_overview_time_series:
            series.append(
                LegacyTimeSeries.from_forecast_overview_series(forecast_series)
            )
        for observation_series in observation_overview_time_series:
            series.append(
                LegacyTimeSeries.from_historical_overview_series(observation_series)
            )
        return LegacyTimeSeriesList(series=series)


@router.get("/time-series/{coverage_identifier}", response_model=TimeSeriesList)
def get_time_series(
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    http_client: Annotated[httpx.Client, Depends(dependencies.get_sync_http_client)],
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
    coverage_data_smoothing: Annotated[
        list[CoverageTimeSeriesProcessingMethod], Query()
    ] = [CoverageTimeSeriesProcessingMethod.NO_PROCESSING],  # noqa
    observation_data_smoothing: Annotated[
        list[ObservationTimeSeriesProcessingMethod], Query()
    ] = [ObservationTimeSeriesProcessingMethod.NO_PROCESSING],  # noqa
    include_coverage_uncertainty: bool = False,
    include_coverage_related_data: bool = False,
):
    """Get dataset time series for a geographic location."""
    if coverage_identifier.split("-")[0] == "forecast":
        coverage = db.get_forecast_coverage(db_session, coverage_identifier)
    else:
        coverage = None
    if coverage is not None:
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
            temporal_range = operations.parse_temporal_range(datetime)
            (
                coverage_series,
                observations_series,
            ) = timeseries.get_forecast_coverage_time_series(
                settings=settings,
                session=db_session,
                http_client=http_client,
                coverage=coverage,
                point_geom=point_geom,
                temporal_range=temporal_range,
                forecast_coverage_processing_methods=coverage_data_smoothing,
                observation_processing_methods=observation_data_smoothing,
                include_coverage_data=include_coverage_data,
                include_observation_data=include_observation_data,
                include_coverage_uncertainty=include_coverage_uncertainty,
                include_coverage_related_models=include_coverage_related_data,
            )
        except exceptions.CoverageDataRetrievalError as err:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not retrieve data",
            ) from err
        else:
            series = []
            for forecast_cov_series in coverage_series:
                series.append(TimeSeries.from_forecast_data_series(forecast_cov_series))
            if observations_series is not None:
                for obs_station_series in observations_series:
                    series.append(
                        TimeSeries.from_observation_station_data_series(
                            obs_station_series
                        )
                    )
            return TimeSeriesList(series=series)
    else:
        raise HTTPException(
            status_code=400, detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL
        )


@router.get(
    "/forecast-variable-combinations",
    response_model=LegacyForecastVariableCombinationsList,
)
def get_forecast_variable_combinations(
    db_session: Annotated[Session, Depends(dependencies.get_db_session)],
):
    sections = get_forecast_advanced_section_navigation(db_session)
    return LegacyForecastVariableCombinationsList(
        combinations=[
            LegacyForecastVariableCombinations.from_navigation_section(s)
            for s in sections
        ],
        translations=LegacyForecastMenuTranslations.from_navigation_sections(sections),
    )
