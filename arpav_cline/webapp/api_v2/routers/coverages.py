import datetime as dt
import logging
import urllib.parse
from xml.etree import ElementTree as et
from typing import (
    Annotated,
    Optional,
    Union,
)

import anyio.to_thread
import httpx
import pydantic
import shapely
import shapely.io
import shapely.errors
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from fastapi.responses import (
    FileResponse,
    StreamingResponse,
)
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
from ....schemas.analytics import (
    ForecastCoverageDownloadRequestCreate,
    HistoricalCoverageDownloadRequestCreate,
    TimeSeriesDownloadRequestCreate,
)
from ....schemas.coverages import (
    HistoricalCoverageInternal,
    ForecastCoverageInternal,
)
from ....schemas.climaticindicators import ClimaticIndicator
from ....schemas.legacy import (
    parse_legacy_aggregation_period,
    CoverageDataSmoothingStrategy,
    ObservationDataSmoothingStrategy,
)
from ....schemas.static import (
    AggregationPeriod,
    CoverageTimeSeriesProcessingMethod,
    DataCategory,
    ForecastScenario,
    ForecastYearPeriod,
    HistoricalDecade,
    HistoricalReferencePeriod,
    HistoricalYearPeriod,
    ObservationTimeSeriesProcessingMethod,
    MeasureType,
)
from ....schemas.dataseries import MannKendallParameters
from ... import dependencies
from ..schemas.analytics import TimeSeriesDownloadRequestRead
from ..schemas.coverages import (
    ForecastCoverageDownloadList,
    HistoricalCoverageDownloadList,
    LegacyConfigurationParameterList,
    LegacyCoverageList,
    LegacyCoverageConfigurationList,
    LegacyForecastCoverageConfigurationReadDetail,
    LegacyHistoricalCoverageConfigurationReadDetail,
    LegacyForecastCoverageReadDetail,
    LegacyHistoricalCoverageReadDetail,
)
from ..schemas.timeseries import (
    LegacyTimeSeries,
    LegacyTimeSeriesList,
)
from ...frontendutils.schemas import (
    LegacyForecastVariableCombinationsList,
    LegacyForecastVariableCombinations,
    LegacyForecastMenuTranslations,
    LegacyHistoricalVariableCombinationsList,
    LegacyHistoricalVariableCombinations,
    LegacyHistoricalMenuTranslations,
)
from ...frontendutils.navigation import (
    get_forecast_advanced_section_navigation,
    get_historical_advanced_section_navigation,
)


logger = logging.getLogger(__name__)
router = APIRouter()

_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL = "Invalid coverage identifier"
_INVALID_COVERAGE_CONFIGURATION_IDENTIFIER_ERROR_DETAIL = (
    "Invalid coverage configuration identifier"
)


@router.get(
    "/configuration-parameters",
    response_model=LegacyConfigurationParameterList,
)
def legacy_list_configuration_parameters(
    request: Request,
    session: Annotated[Session, Depends(dependencies.get_db_session)],
    list_params: Annotated[dependencies.CommonListFilterParameters, Depends()],
    name_contains: str | None = None,
):
    """List coverage-related configuration parameters.

    Lists configuration parameters which can be used when filtering for coverages.
    """
    config_params, filtered_total = db.legacy_list_configuration_parameters(
        session,
        limit=list_params.limit,
        offset=list_params.offset,
        include_total=True,
        name_filter=name_contains,
    )
    _, unfiltered_total = db.legacy.legacy_list_configuration_parameters(
        session, limit=1, offset=0, include_total=True
    )
    return LegacyConfigurationParameterList.from_items(
        config_params,
        request,
        limit=list_params.limit,
        offset=list_params.offset,
        filtered_total=filtered_total,
        unfiltered_total=unfiltered_total,
    )


@router.get(
    "/coverage-configurations",
    response_model=LegacyCoverageConfigurationList,
)
def legacy_list_coverage_configurations(
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
    unfiltered_forecast_cov_confs = (
        db.legacy_collect_all_forecast_coverage_configurations(session)
    )
    unfiltered_historical_cov_confs = (
        db.legacy_collect_all_historical_coverage_configurations(session)
    )
    if include_forecasts:
        filtered_forecast_cov_confs = (
            db.legacy_collect_all_forecast_coverage_configurations(
                session, conf_param_filter=filter_values
            )
        )
    if include_historical:
        filtered_historical_cov_confs = (
            db.legacy_collect_all_historical_coverage_configurations(
                session, conf_param_filter=filter_values
            )
        )

    return LegacyCoverageConfigurationList.from_items(
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
    "/coverage-configurations/{coverage_configuration_identifier}",
    response_model=Union[
        LegacyForecastCoverageConfigurationReadDetail,
        LegacyHistoricalCoverageConfigurationReadDetail,
    ],
)
def legacy_get_coverage_configuration(
    request: Request,
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    session: Annotated[Session, Depends(dependencies.get_db_session)],
    coverage_configuration_identifier: str,
):
    """Return details about a coverage configuration."""
    try:
        category = DataCategory(coverage_configuration_identifier.partition("-")[0])
    except ValueError:
        raise HTTPException(
            400, detail=_INVALID_COVERAGE_CONFIGURATION_IDENTIFIER_ERROR_DETAIL
        )
    else:
        if category in (DataCategory.FORECAST, DataCategory.HISTORICAL):
            if category == DataCategory.FORECAST:
                cov_conf = db.get_forecast_coverage_configuration_by_identifier(
                    session, coverage_configuration_identifier
                )
                coverages = db.generate_forecast_coverages_from_configuration(cov_conf)
                response_model = LegacyForecastCoverageConfigurationReadDetail
            else:  # historical
                cov_conf = db.get_historical_coverage_configuration_by_identifier(
                    session, coverage_configuration_identifier
                )
                coverages = db.generate_historical_coverages_from_configuration(
                    cov_conf
                )
                response_model = LegacyHistoricalCoverageConfigurationReadDetail

            return response_model.from_db_instance(
                cov_conf,
                coverages,
                _get_palette_colors(cov_conf.climatic_indicator, settings),
                request,
            )

        else:
            raise HTTPException(
                400, detail=_INVALID_COVERAGE_CONFIGURATION_IDENTIFIER_ERROR_DETAIL
            )


def _get_palette_colors(
    climatic_indicator: ClimaticIndicator,
    settings: ArpavPpcvSettings,
) -> list[tuple[float, str]]:
    palette_colors = palette.parse_palette(
        climatic_indicator.palette, settings.palettes_dir
    )
    applied_colors = []
    if palette_colors is not None:
        minimum = climatic_indicator.color_scale_min
        maximum = climatic_indicator.color_scale_max
        if abs(maximum - minimum) > 0.001:
            applied_colors = palette.apply_palette(
                palette_colors,
                minimum,
                maximum,
                num_stops=settings.palette_num_stops,
            )
        else:
            logger.warning(
                f"Cannot calculate applied colors for climatic indicator "
                f"{climatic_indicator.identifier!r}"
            )
    else:
        logger.warning(f"Unable to parse palette " f"{climatic_indicator.palette!r}")
    return applied_colors


@router.get(
    "/coverages",
    response_model=LegacyCoverageList,
)
def legacy_list_coverages(
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
    """List coverages"""
    filter_values = operations.convert_conf_params_filter(session, possible_value or [])
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

    filtered_forecast_covs = []
    filtered_historical_covs = []
    total_filtered_forecast_covs = 0
    total_filtered_historical_covs = 0
    _, total_unfiltered_forecast_covs = db.legacy_list_forecast_coverages(
        session, include_total=True
    )
    _, total_unfiltered_historical_covs = db.legacy_list_historical_coverages(
        session, include_total=True
    )
    if include_forecasts:
        (
            filtered_forecast_covs,
            total_filtered_forecast_covs,
        ) = db.legacy_list_forecast_coverages(
            session, conf_param_filter=filter_values, include_total=True
        )
    if include_historical:
        (
            filtered_historical_covs,
            total_filtered_historical_covs,
        ) = db.legacy_list_historical_coverages(
            session, conf_param_filter=filter_values, include_total=True
        )
    return LegacyCoverageList.from_items(
        filtered_forecast_covs,
        filtered_historical_covs,
        request,
        limit=list_params.limit,
        offset=list_params.offset,
        filtered_total_forecast_coverages=total_filtered_forecast_covs,
        filtered_total_historical_coverages=total_filtered_historical_covs,
        unfiltered_total_forecast_coverages=total_unfiltered_forecast_covs,
        unfiltered_total_historical_coverages=total_unfiltered_historical_covs,
    )


@router.get(
    "/coverages/{coverage_identifier}",
    response_model=Union[
        LegacyHistoricalCoverageReadDetail,
        LegacyForecastCoverageReadDetail,
    ],
)
def legacy_get_coverage(
    request: Request,
    session: Annotated[Session, Depends(dependencies.get_db_session)],
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    coverage_identifier: str,
):
    """Get coverage details"""
    try:
        category = DataCategory(coverage_identifier.partition("-")[0])
    except ValueError:
        raise HTTPException(400, detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL)
    else:
        if category in (DataCategory.FORECAST, DataCategory.HISTORICAL):
            if category == DataCategory.FORECAST:
                cov = db.get_forecast_coverage(session, coverage_identifier)
                response_model = LegacyForecastCoverageReadDetail
            else:  # historical
                cov = db.get_historical_coverage(session, coverage_identifier)
                response_model = LegacyHistoricalCoverageReadDetail
            if cov is not None:
                return response_model.from_db_instance(
                    cov,
                    request,
                    settings,
                    _get_palette_colors(cov.configuration.climatic_indicator, settings),
                )
            else:
                raise HTTPException(
                    400, detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL
                )
        else:
            raise HTTPException(
                400, detail=_INVALID_COVERAGE_CONFIGURATION_IDENTIFIER_ERROR_DETAIL
            )


@router.get(
    "/coverage-identifiers",
    response_model=LegacyCoverageList,
    deprecated=True,
)
def deprecated_list_coverage_identifiers(
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
    """List coverages.

    Use the `/coverages/coverages` endpoint instead
    """
    return legacy_list_coverages(request, session, list_params, possible_value)


@router.get(
    "/coverage-identifiers/{coverage_identifier}",
    response_model=Union[
        LegacyHistoricalCoverageReadDetail,
        LegacyForecastCoverageReadDetail,
    ],
    deprecated=True,
)
def deprecated_get_coverage_identifier(
    request: Request,
    session: Annotated[Session, Depends(dependencies.get_db_session)],
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    coverage_identifier: str,
):
    """Get coverage details.

    Use the /coverages/coverages/{coverage_identifier} endpoint instead.
    """
    return legacy_get_coverage(request, session, settings, coverage_identifier)


@router.get("/wms/{coverage_identifier}")
async def wms_endpoint(
    request: Request,
    session: Annotated[Session, Depends(dependencies.get_db_session)],
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    http_client: Annotated[httpx.AsyncClient, Depends(dependencies.get_http_client)],
    coverage_identifier: str,
    version: str = "1.3.0",
):
    """### Serve coverage via OGC Web Map Service.

    Pass additional relevant WMS query parameters directly to this endpoint.
    """
    query_params = {k.lower(): v for k, v in request.query_params.items()}
    if query_params.get("request") == "GetMap" and query_params.get("opacity") == "0":
        logger.debug(
            "Bypassing THREDDS server and returning a pre-rendered transparent "
            "image..."
        )
        size_ = query_params.get("width", "256")
        image_path = settings.transparent_images_dir / f"transparent-{size_}.png"
        response = FileResponse(image_path)
    else:
        try:
            category = DataCategory(coverage_identifier.partition("-")[0])
        except ValueError:
            raise HTTPException(400, detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL)
        else:
            if category in (DataCategory.FORECAST, DataCategory.HISTORICAL):
                if category == DataCategory.FORECAST:
                    cov = db.get_forecast_coverage(session, coverage_identifier)
                else:  # historical
                    cov = db.get_historical_coverage(session, coverage_identifier)
            else:
                raise HTTPException(
                    400, detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL
                )
            if cov is not None:
                base_wms_url = cov.get_wms_base_url(settings.thredds_server)
                parsed_url = urllib.parse.urlparse(base_wms_url)
                logger.info(f"{base_wms_url=}")
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
                    wms_response = await thredds_utils.proxy_request(
                        wms_url, http_client
                    )
                except httpx.HTTPStatusError as err:
                    logger.exception(
                        msg=f"THREDDS server replied with an error: {err.response.text}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=err.response.text,
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
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL,
                )
    return response


@router.get("/forecast-data", response_model=ForecastCoverageDownloadList)
def list_forecast_data_download_links(
    request: Request,
    session: Annotated[Session, Depends(dependencies.get_db_session)],
    list_params: Annotated[dependencies.CommonListFilterParameters, Depends()],
    climatological_variable: Annotated[list[str], Query()] = None,
    aggregation_period: Annotated[list[str], Query()] = None,
    measure: Annotated[list[MeasureType], Query()] = None,
    climatological_model: Annotated[list[str], Query()] = None,
    scenario: Annotated[list[ForecastScenario], Query()] = None,
    year_period: Annotated[list[ForecastYearPeriod], Query()] = None,
    time_window: Annotated[list[str], Query()] = None,
) -> ForecastCoverageDownloadList:
    """Get download links forecast data"""
    aggregation_period_filter = (
        [parse_legacy_aggregation_period(ap) for ap in aggregation_period]
        if aggregation_period
        else None
    )
    coverages = db.collect_all_forecast_coverages(
        session,
        climatological_variable_filter=climatological_variable,
        aggregation_period_filter=aggregation_period_filter,
        climatological_model_filter=climatological_model,
        scenario_filter=scenario,
        measure_filter=measure,
        year_period_filter=year_period,
        time_window_filter=time_window,
    )

    return ForecastCoverageDownloadList.from_items(
        coverages=coverages,
        request=request,
        limit=list_params.limit,
        offset=list_params.offset,
        total=len(coverages),
    )


@router.get("/forecast-data/{coverage_identifier}")
async def get_forecast_data(
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    http_client: Annotated[httpx.AsyncClient, Depends(dependencies.get_http_client)],
    session: Annotated[Session, Depends(dependencies.get_db_session)],
    coverage_identifier: str,
    analytics_params: Annotated[dependencies.DownloadAnalyticsParameters, Depends()],
    coords: Annotated[str, Query(description="A Well-Known-Text Polygon")] = None,
    datetime: Optional[str] = "../..",
):
    """Return forecast coverages in their native NetCDF format"""
    if (coverage := db.get_forecast_coverage(session, coverage_identifier)) is not None:
        await anyio.to_thread.run_sync(
            db.create_forecast_coverage_download_request,
            session,
            ForecastCoverageDownloadRequestCreate(
                request_datetime=dt.datetime.now(tz=dt.timezone.utc),
                entity_name=analytics_params.entity_name,
                is_public_sector=analytics_params.is_public_sector,
                download_reason=analytics_params.download_reason,
                climatological_variable=coverage.configuration.climatic_indicator.name,
                aggregation_period=coverage.configuration.climatic_indicator.aggregation_period.value,
                measure_type=coverage.configuration.climatic_indicator.measure_type.value,
                year_period=coverage.year_period.value,
                climatological_model=coverage.forecast_model.name,
                scenario=coverage.scenario.value,
                time_window=(
                    coverage.forecast_time_window.name
                    if coverage.forecast_time_window
                    else None
                ),
            ),
        )
        return await _get_coverage_data(
            settings, http_client, coverage, coords, datetime
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL,
        )


@router.get(
    "/historical-data",
    response_model=HistoricalCoverageDownloadList,
)
def list_historical_data_download_links(
    request: Request,
    session: Annotated[Session, Depends(dependencies.get_db_session)],
    list_params: Annotated[dependencies.CommonListFilterParameters, Depends()],
    climatological_variable: Annotated[list[str], Query()] = None,
    aggregation_period: Annotated[list[str], Query()] = None,
    measure: Annotated[list[MeasureType], Query()] = None,
    year_period: Annotated[list[HistoricalYearPeriod], Query()] = None,
    decade: Annotated[list[HistoricalDecade], Query()] = None,
    reference_period: Annotated[list[HistoricalReferencePeriod], Query()] = None,
) -> HistoricalCoverageDownloadList:
    """Get download links for historical data"""
    aggregation_period_filter = (
        [parse_legacy_aggregation_period(ap) for ap in aggregation_period]
        if aggregation_period
        else None
    )
    coverages = db.collect_all_historical_coverages(
        session,
        climatological_variable_filter=climatological_variable,
        aggregation_period_filter=aggregation_period_filter,
        measure_filter=measure,
        year_period_filter=year_period,
        reference_period_filter=reference_period,
        decade_filter=decade,
    )

    return HistoricalCoverageDownloadList.from_items(
        coverages=coverages,
        request=request,
        limit=list_params.limit,
        offset=list_params.offset,
        total=len(coverages),
    )


@router.get("/historical-data/{coverage_identifier}")
async def get_historical_data(
    settings: Annotated[ArpavPpcvSettings, Depends(dependencies.get_settings)],
    http_client: Annotated[httpx.AsyncClient, Depends(dependencies.get_http_client)],
    session: Annotated[Session, Depends(dependencies.get_db_session)],
    analytics_params: Annotated[dependencies.DownloadAnalyticsParameters, Depends()],
    coverage_identifier: str,
    coords: Annotated[str, Query(description="A Well-Known-Text Polygon")] = None,
    datetime: Optional[str] = "../..",
):
    """Return historical coverages in their native NetCDF format"""
    if (
        coverage := db.get_historical_coverage(session, coverage_identifier)
    ) is not None:
        await anyio.to_thread.run_sync(
            db.create_historical_coverage_download_request,
            session,
            HistoricalCoverageDownloadRequestCreate(
                request_datetime=dt.datetime.now(tz=dt.timezone.utc),
                entity_name=analytics_params.entity_name,
                is_public_sector=analytics_params.is_public_sector,
                download_reason=analytics_params.download_reason,
                climatological_variable=coverage.configuration.climatic_indicator.name,
                aggregation_period=coverage.configuration.climatic_indicator.aggregation_period.value,
                measure_type=coverage.configuration.climatic_indicator.measure_type.value,
                year_period=coverage.year_period.value,
                decade=coverage.decade.value if coverage.decade else None,
                reference_period=(
                    coverage.configuration.reference_period.value
                    if coverage.configuration.reference_period
                    else None
                ),
            ),
        )
        return await _get_coverage_data(
            settings, http_client, coverage, coords, datetime
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL,
        )


async def _get_coverage_data(
    settings: ArpavPpcvSettings,
    http_client: httpx.AsyncClient,
    coverage: Union[ForecastCoverageInternal, HistoricalCoverageInternal],
    coords: Annotated[str, Query(description="A Well-Known-Text Polygon")] = None,
    datetime: Optional[str] = "../..",
):
    if coverage.configuration.climatic_indicator.aggregation_period in (
        AggregationPeriod.THIRTY_YEAR,
        AggregationPeriod.TEN_YEAR,
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
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid coords - {exc}",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid coords - Must be a WKT Polygon",
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
    response_model=LegacyTimeSeriesList,
)
def get_overview_time_series(
    session: Annotated[Session, Depends(dependencies.get_db_session)],
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
            session=session,
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


@router.get(
    "/time-series/{coverage_identifier}",
    response_model=LegacyTimeSeriesList,
    deprecated=True,
)
def deprecated_get_time_series(
    session: Annotated[Session, Depends(dependencies.get_db_session)],
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
    coverage_data_smoothing: Annotated[list[CoverageDataSmoothingStrategy], Query()] = [
        CoverageDataSmoothingStrategy.NO_SMOOTHING
    ],  # noqa
    observation_data_smoothing: Annotated[
        list[ObservationDataSmoothingStrategy], Query()
    ] = [ObservationDataSmoothingStrategy.NO_SMOOTHING],  # noqa
    include_coverage_uncertainty: bool = False,
    include_coverage_related_data: bool = False,
):
    """Get forecast dataset time series for a geographic location.

    Use the `/coverages/forecast-time-series/{coverage_identifier}` endpoint instead.
    """
    return get_forecast_time_series(
        session=session,
        settings=settings,
        http_client=http_client,
        coverage_identifier=coverage_identifier,
        coords=coords,
        datetime=datetime,
        include_coverage_data=include_coverage_data,
        include_observation_data=include_observation_data,
        coverage_data_smoothing=coverage_data_smoothing,
        observation_data_smoothing=observation_data_smoothing,
        include_coverage_uncertainty=include_coverage_uncertainty,
        include_coverage_related_data=include_coverage_related_data,
    )


@router.get(
    "/forecast-time-series/{coverage_identifier}",
    # response_model=TimeSeriesList,
    response_model=LegacyTimeSeriesList,
)
def get_forecast_time_series(
    session: Annotated[Session, Depends(dependencies.get_db_session)],
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
    coverage_data_smoothing: Annotated[list[CoverageDataSmoothingStrategy], Query()] = [
        CoverageDataSmoothingStrategy.NO_SMOOTHING
    ],  # noqa
    observation_data_smoothing: Annotated[
        list[ObservationDataSmoothingStrategy], Query()
    ] = [ObservationDataSmoothingStrategy.NO_SMOOTHING],  # noqa
    include_coverage_uncertainty: bool = False,
    include_coverage_related_data: bool = False,
):
    """Get forecast dataset time series for a geographic location"""
    try:
        data_category = DataCategory(coverage_identifier.partition("-")[0])
    except ValueError:
        raise HTTPException(400, detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL)
    if data_category != DataCategory.FORECAST:
        raise HTTPException(400, detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL)
    if (coverage := db.get_forecast_coverage(session, coverage_identifier)) is not None:
        # converting from legacy data_smoothing enum
        coverage_processing_methods = [
            cs.to_processing_method() for cs in coverage_data_smoothing
        ]
        observation_processing_methods = [
            os.to_processing_method() for os in observation_data_smoothing
        ]

        try:
            point_geom = _get_point_location(coords)
        except shapely.errors.GEOSException as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
            )
        temporal_range = operations.parse_temporal_range(datetime)
        try:
            (
                forecast_series,
                observations_series,
            ) = timeseries.get_forecast_coverage_time_series(
                settings=settings,
                session=session,
                http_client=http_client,
                coverage=coverage,
                point_geom=point_geom,
                temporal_range=temporal_range,
                coverage_processing_methods=coverage_processing_methods,
                observation_processing_methods=observation_processing_methods,
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
            for forecast_cov_series in forecast_series:
                series.append(
                    LegacyTimeSeries.from_forecast_data_series(forecast_cov_series)
                )
            if observations_series is not None:
                for obs_station_series in observations_series:
                    series.append(
                        LegacyTimeSeries.from_observation_station_data_series(
                            obs_station_series
                        )
                    )
            return LegacyTimeSeriesList(series=series)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL,
        )


@router.get(
    "/historical-time-series/{coverage_identifier}",
    response_model=LegacyTimeSeriesList,
)
def get_historical_time_series(
    session: Annotated[Session, Depends(dependencies.get_db_session)],
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
    coverage_processing_methods: Annotated[
        list[Union[CoverageTimeSeriesProcessingMethod,]], Query()
    ] = [CoverageTimeSeriesProcessingMethod.NO_PROCESSING],  # noqa
    mann_kendall_start_year: Optional[int] = None,
    mann_kendall_end_year: Optional[int] = None,
    observation_processing_methods: Annotated[
        list[ObservationTimeSeriesProcessingMethod], Query()
    ] = [ObservationTimeSeriesProcessingMethod.NO_PROCESSING],  # noqa
):
    """Get historical dataset time series for a geographic location."""
    try:
        data_category = DataCategory(coverage_identifier.partition("-")[0])
    except ValueError:
        raise HTTPException(400, detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL)
    if data_category != DataCategory.HISTORICAL:
        raise HTTPException(400, detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL)
    if (
        coverage := db.get_historical_coverage(session, coverage_identifier)
    ) is not None:
        logger.debug(f"found coverage {coverage.identifier=}")
        cov_methods = coverage_processing_methods
        if all((mann_kendall_start_year, mann_kendall_end_year)):
            mann_kendall_params = MannKendallParameters(
                start_year=mann_kendall_start_year,
                end_year=mann_kendall_end_year,
            )
            if CoverageTimeSeriesProcessingMethod.MANN_KENDALL_TREND in cov_methods:
                cov_methods = [
                    pm
                    if pm != CoverageTimeSeriesProcessingMethod.MANN_KENDALL_TREND
                    else (pm, mann_kendall_params)
                    for pm in coverage_processing_methods
                ]
        try:
            point_geom = _get_point_location(coords)
        except shapely.errors.GEOSException as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
            )
        temporal_range = operations.parse_temporal_range(datetime)
        try:
            (
                coverage_series,
                observations_series,
            ) = timeseries.get_historical_coverage_time_series(
                settings=settings,
                session=session,
                http_client=http_client,
                coverage=coverage,
                point_geom=point_geom,
                temporal_range=temporal_range,
                coverage_processing_methods=cov_methods,
                observation_processing_methods=observation_processing_methods,
                include_coverage_data=include_coverage_data,
                include_observation_data=include_observation_data,
            )
        except exceptions.CoverageDataRetrievalError as err:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not retrieve data",
            ) from err
        else:
            time_series = []
            for series in coverage_series:
                time_series.append(LegacyTimeSeries.from_historical_data_series(series))
            if observations_series is not None:
                for obs_station_series in observations_series:
                    time_series.append(
                        LegacyTimeSeries.from_observation_station_data_series(
                            obs_station_series
                        )
                    )
            return LegacyTimeSeriesList(series=time_series)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL,
        )


def _get_point_location(raw_coords: str) -> shapely.Point:
    geom = shapely.io.from_wkt(raw_coords)
    if geom.geom_type == "MultiPoint":
        logger.warning(
            f"Expected coords parameter to be a WKT Point but "
            f"got {geom.geom_type!r} instead - Using the first point"
        )
        point_geom = geom.geoms[0].centroid
    elif geom.geom_type == "Point":
        point_geom = geom
    else:
        logger.warning(
            f"Expected coords parameter to be a WKT Point but "
            f"got {geom.geom_type!r} instead - Using the centroid instead"
        )
        point_geom = geom.centroid
    return point_geom


@router.get(
    "/forecast-variable-combinations",
    response_model=LegacyForecastVariableCombinationsList,
)
def get_forecast_variable_combinations(
    session: Annotated[Session, Depends(dependencies.get_db_session)],
):
    """Return valid combinations of parameters used to describe forecast data."""
    sections = get_forecast_advanced_section_navigation(session)
    return LegacyForecastVariableCombinationsList(
        combinations=[
            LegacyForecastVariableCombinations.from_navigation_section(s)
            for s in sections
        ],
        translations=LegacyForecastMenuTranslations.from_navigation_sections(sections),
    )


@router.get(
    "/historical-variable-combinations",
    response_model=LegacyHistoricalVariableCombinationsList,
)
def get_historical_variable_combinations(
    session: Annotated[Session, Depends(dependencies.get_db_session)],
):
    """Return valid combinations of parameters used to describe historical data."""
    sections = get_historical_advanced_section_navigation(session)
    return LegacyHistoricalVariableCombinationsList(
        combinations=[
            LegacyHistoricalVariableCombinations.from_navigation_section(s)
            for s in sections
        ],
        translations=LegacyHistoricalMenuTranslations.from_navigation_sections(
            sections
        ),
    )


@router.get(
    "/time-series-download-request/{coverage_identifier}",
    response_model=TimeSeriesDownloadRequestRead,
)
def notify_time_series_download_request(
    session: Annotated[Session, Depends(dependencies.get_db_session)],
    coverage_identifier: str,
    analytics_params: Annotated[dependencies.DownloadAnalyticsParameters, Depends()],
    coords: Annotated[str, Query(max_length=20)],
) -> TimeSeriesDownloadRequestRead:
    """Notify backend of a download request for time series data for a coverage."""
    raw_category = coverage_identifier.split("-")[0]
    try:
        data_category = DataCategory(raw_category)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL,
        )
    else:
        if data_category == DataCategory.FORECAST:
            cov = db.get_forecast_coverage(session, coverage_identifier)
        else:
            cov = db.get_historical_coverage(session, coverage_identifier)
        if cov is not None:
            geom = shapely.io.from_wkt(coords)
            download_request_create = TimeSeriesDownloadRequestCreate(
                request_datetime=dt.datetime.now(tz=dt.timezone.utc),
                entity_name=analytics_params.entity_name,
                is_public_sector=analytics_params.is_public_sector,
                download_reason=analytics_params.download_reason,
                climatological_variable=cov.configuration.climatic_indicator.name,
                aggregation_period=cov.configuration.climatic_indicator.aggregation_period.value,
                measure_type=cov.configuration.climatic_indicator.measure_type.value,
                year_period=cov.year_period.value,
                data_category=data_category.value,
                longitude=geom.centroid.x,
                latitude=geom.centroid.y,
            )
            download_request = db.create_time_series_download_request(
                session, download_request_create
            )
            return TimeSeriesDownloadRequestRead(**download_request.model_dump())
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=_INVALID_COVERAGE_IDENTIFIER_ERROR_DETAIL,
            )
