import json
import uuid
import urllib.parse
from pathlib import Path
from typing import (
    Iterable,
    Literal,
    Union,
    cast,
)

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.gridspec import GridSpec
import numpy as np

from qgis.PyQt import (
    QtCore,
    QtGui,
    QtNetwork,
)
from qgis.core import (
    Qgis,
    QgsExpressionContextUtils,
    QgsLayout,
    QgsPrintLayout,
    QgsLayoutItem,
    QgsLayoutItemMap,
    QgsLayoutItemPicture,
    QgsLayerTree,
    QgsLayerTreeGroup,
    QgsMapLayer,
    QgsMarkerSymbol,
    QgsMessageLog,
    QgsNetworkAccessManager,
    QgsProject,
    QgsRasterLayer,
    QgsSymbol,
    QgsVectorTileBasicRenderer,
    QgsVectorTileBasicRendererStyle,
    QgsVectorTileLayer,
)
from qgis.server import (
    QgsServerInterface,
    QgsServerRequest,
    QgsServerResponse,
    QgsService,
)

from . import models

logger = QgsMessageLog.logMessage


class ClinePrinterException(Exception):
    ...


class ClinePrinterServer:
    def __init__(self, server_iface: QgsServerInterface):
        service_registry = server_iface.serviceRegistry()
        printer_service = ClinePrinterService(server_iface)
        service_registry.registerService(printer_service)


class ClinePrinterService(QgsService):
    server_iface: QgsServerInterface
    network_access_manager: QgsNetworkAccessManager
    forecast_layout_name = "map-printer-forecast"
    historical_layout_name = "map-printer-historical"
    vector_tile_layer_name = "observation_stations"
    webapp_service_internal_base_url = "http://webapp:5001"
    vector_tile_service_internal_base_url = "http://martin:3000"
    osm_layer_name = "osm_standard"
    municipalities_layer_name = "municipalities"
    extent = {
        "xmin": 1017823,
        "ymin": 5574459,
        "xmax": 1690978,
        "ymax": 5970564,
    }

    def __init__(self, server_iface: QgsServerInterface, *args, **kwargs):
        self.server_iface = server_iface
        self.network_access_manager = QgsNetworkAccessManager().instance()
        self.network_access_manager.setRequestPreprocessor(add_cache_load_control)
        super().__init__(*args, **kwargs)

    def name(self) -> str:
        return "CLINE_PRINTER"

    def version(self) -> str:
        return "1.0.0"

    def executeRequest(
        self,
        request: QgsServerRequest,
        response: QgsServerResponse,
        project: QgsProject | None,
    ):
        original_params = request.parameters()
        logger(f"{original_params=}")
        request_id = original_params.get("REQUEST_ID", str(uuid.uuid4()))
        unload_layers(project, self.osm_layer_name, self.municipalities_layer_name)
        try:
            cov_identifier = original_params.get("COVERAGE_IDENTIFIER")
            if cov_identifier is None:
                raise ClinePrinterException("Missing COVERAGE_IDENTIFIER parameter")
            wms_layer_name = original_params.get("WMS_LAYER_NAME")
            if wms_layer_name is None:
                write_error(response, "Missing WMS_LAYER_NAME parameter")
        except ClinePrinterException as err:
            write_error(response, str(err))
        else:
            language_code = original_params.get("LANGUAGE_CODE", "it")
            try:
                api_details = self.get_api_details(cov_identifier)
            except ClinePrinterException as err:
                write_error(response, str(err))
            else:
                data_category = cov_identifier.partition("-")[0]
                if data_category in ("forecast", "historical"):
                    if data_category == "forecast":
                        self.adjust_forecast_print_layout(
                            api_details,
                            language_code,
                            wms_layer_name,
                            project,
                            request_id,
                        )
                    else:
                        self.adjust_historical_print_layout(
                            api_details,
                            language_code,
                            wms_layer_name,
                            project,
                            request_id,
                        )
                else:
                    write_error(response, f"Unknown data category {data_category!r}")
                return call_wms_get_print(
                    request=request,
                    response=response,
                    qgis_project=project,
                    server_iface=self.server_iface,
                    layout_name=self._select_layout(data_category),
                    extent=self.extent,
                )

    def _select_layout(self, data_category: str) -> str:
        return (
            self.forecast_layout_name
            if data_category == "forecast"
            else self.historical_layout_name
        )

    def adjust_forecast_print_layout(
        self,
        api_details: models.RawApiDetails,
        language_code: str,
        wms_layer_name: str,
        project: QgsProject,
        request_id: str,
    ):
        layout_variables = models.ForecastMapLayoutVariables.from_api_details(
            api_details, language_code
        )
        return adjust_print_layout(
            layout_name=self.forecast_layout_name,
            coverage_details=api_details.coverage,
            layout_variables=layout_variables,
            wms_layer_name=wms_layer_name,
            vector_tile_layer_name=self.vector_tile_layer_name,
            osm_layer_name=self.osm_layer_name,
            municipalities_layer_name=self.municipalities_layer_name,
            qgis_project=project,
            internal_wms_url_base=self.webapp_service_internal_base_url,
            internal_vector_tiles_url_base=(self.vector_tile_service_internal_base_url),
            request_id=request_id,
        )

    def adjust_historical_print_layout(
        self,
        api_details: models.RawApiDetails,
        language_code: str,
        wms_layer_name: str,
        project: QgsProject,
        request_id: str,
    ):
        layout_variables = models.HistoricalMapLayoutVariables.from_api_details(
            api_details, language_code
        )
        return adjust_print_layout(
            layout_name=self.historical_layout_name,
            coverage_details=api_details.coverage,
            layout_variables=layout_variables,
            wms_layer_name=wms_layer_name,
            vector_tile_layer_name=self.vector_tile_layer_name,
            osm_layer_name=self.osm_layer_name,
            municipalities_layer_name=self.municipalities_layer_name,
            qgis_project=project,
            internal_wms_url_base=self.webapp_service_internal_base_url,
            internal_vector_tiles_url_base=(self.vector_tile_service_internal_base_url),
            request_id=request_id,
        )

    def get_api_details(self, coverage_identifier: str) -> models.RawApiDetails:
        cov_details = get_arpav_cline_details(
            (
                f"{self.webapp_service_internal_base_url}/api/v2"
                f"/coverages/coverages/{coverage_identifier}"
            ),
            self.network_access_manager,
        )
        conf_parameters_details = get_arpav_cline_details(
            (
                f"{self.webapp_service_internal_base_url}/api/v2/"
                f"coverages/configuration-parameters"
            ),
            self.network_access_manager,
        )["items"]
        climatic_indicator_details = get_arpav_cline_details(
            (
                f"{self.webapp_service_internal_base_url}/api/v2"
                f"/climatic-indicators/"
                f"{cov_details['climatic_indicator_url'].rpartition('/')[-1]}"
            ),
            self.network_access_manager,
        )
        return models.RawApiDetails(
            coverage=cov_details,
            configuration_parameters=conf_parameters_details,
            climatic_indicator=climatic_indicator_details,
        )


def add_cache_load_control(request: QtNetwork.QNetworkRequest):
    """Prevents QGIS from caching network requests.

    This is a workaround for the fact that QGIS Server is not being able
    to cache WMS requests properly, as discussed in:

    https://github.com/qgis/QGIS/issues/59613

    """

    request.setAttribute(
        QtNetwork.QNetworkRequest.CacheLoadControlAttribute,
        QtNetwork.QNetworkRequest.CacheLoadControl.AlwaysNetwork,
    )


def unload_layers(project: QgsProject, *to_keep: str):
    to_remove = []
    for identifier, layer in project.mapLayers().items():
        if layer.name() not in to_keep:
            to_remove.append(identifier)
    project.removeMapLayers(to_remove)


def call_wms_get_print(
    *,
    request: QgsServerRequest,
    response: QgsServerResponse,
    qgis_project: QgsProject,
    server_iface: QgsServerInterface,
    layout_name: str,
    extent: dict[str, int],
) -> None:
    formatted_extent = ",".join(
        (
            str(extent["xmin"]),
            str(extent["ymin"]),
            str(extent["xmax"]),
            str(extent["ymax"]),
        )
    )
    wms_service_name = "WMS"
    wms_version = "1.3.0"
    request.setParameter("SERVICE", wms_service_name)
    request.setParameter("TEMPLATE", layout_name)
    request.setParameter("VERSION", wms_version)
    request.setParameter("REQUEST", "GetPrint")
    request.setParameter("CRS", "EPSG:3857")
    request.setParameter("MAP0:EXTENT", formatted_extent)
    request.setParameter("MAP0:SCALE", "2513142")
    request.removeParameter("CLINE_COVERAGE_IDENTIFIER")
    request.removeParameter("CLINE_WMS_LAYER_NAME")
    request.removeParameter("MAP")
    logger(f"loaded layers: {qgis_project.mapLayers()=}")
    logger(f"modified request parameters: {request.parameters()=}")
    wms_service = server_iface.serviceRegistry().getService(
        wms_service_name, wms_version
    )
    return wms_service.executeRequest(request, response, qgis_project)


def write_error(response: QgsServerResponse, message: str):
    response.write(json.dumps({"detail": message}))
    response.setHeader("Content-Type", "application/json")
    response.setStatusCode(400)
    response.finish()


def adjust_print_layout(
    *,
    layout_name: str,
    coverage_details: dict,
    layout_variables: Union[
        models.ForecastMapLayoutVariables, models.HistoricalMapLayoutVariables
    ],
    wms_layer_name: str,
    vector_tile_layer_name: str,
    osm_layer_name: str,
    municipalities_layer_name: str,
    qgis_project: QgsProject,
    internal_wms_url_base: str,
    internal_vector_tiles_url_base: str,
    request_id: str,
) -> None:
    internal_wms_base_url = "/".join(
        (
            internal_wms_url_base,
            coverage_details["wms_base_url"].replace("://", "").partition("/")[-1],
        )
    )

    logger(f"{internal_wms_base_url=}")
    internal_vector_tile_layer_url = "/".join(
        (
            internal_vector_tiles_url_base,
            coverage_details["observation_stations_vector_tile_layer_url"].partition(
                "vector-tiles/"
            )[-1],
        )
    )
    logger(f"{internal_vector_tile_layer_url=}")
    wms_map_layer = load_cline_wms_layer(
        internal_wms_base_url, wms_layer_name, qgis_project
    )
    vector_tile_map_layer = load_cline_vector_tile_layer(
        internal_vector_tile_layer_url, vector_tile_layer_name, qgis_project
    )
    osm_standard_map_layer = qgis_project.mapLayersByName(osm_layer_name)[0]
    municipalities_map_layer = qgis_project.mapLayersByName(municipalities_layer_name)[
        0
    ]
    layer_order = [
        vector_tile_map_layer,
        municipalities_map_layer,
        wms_map_layer,
        osm_standard_map_layer,
    ]
    layer_tree_root = qgis_project.layerTreeRoot()
    reorder_layers(layer_tree_root, layer_order)
    wms_map_layer.setOpacity(0.9)
    vector_tile_map_layer.setOpacity(1)
    set_vector_tile_layer_color(vector_tile_map_layer, QtGui.QColor(179, 181, 181))
    municipalities_map_layer.setOpacity(0.5)
    layout_manager = qgis_project.layoutManager()
    print_layout = layout_manager.layoutByName(layout_name)
    print_layout = cast(QgsPrintLayout, print_layout)
    map_item: QgsLayoutItem | None = print_layout.itemById("map1")
    if map_item is not None:
        map_item: QgsLayoutItemMap
        map_item.setKeepLayerSet(False)
        map_item.refresh()
    refresh_layout_variables(print_layout, layout_variables)
    # map_info_html_layout_element = print_layout.itemById("map_info").multiFrame()
    # update_layout_item_html(map_info_html_layout_element, coverage_details)
    adjust_legend(
        print_layout,
        coverage_details["legend"]["color_entries"],
        colorbar_path=Path(f"/tmp/cline_printer_legend_{request_id}.svg"),
    )
    print_layout.refresh()


def set_vector_tile_layer_color(
    layer: QgsVectorTileLayer,
    fill_color: QtGui.QColor,
    stroke_color: QtGui.QColor = None,
) -> None:
    renderer = layer.renderer()
    original_styles = renderer.styles()
    new_styles = []
    for old_style in original_styles:
        name = old_style.styleName().lower()
        new_style = QgsVectorTileBasicRendererStyle(old_style)
        if "point" in name or "marker" in name:
            print(f"Processing style {name=}...")
            old_symbol = new_style.symbol()
            if old_symbol.type() == QgsSymbol.SymbolType.Marker:
                print("Creating a new symbol...")
                new_symbol = QgsMarkerSymbol.createSimple(
                    {
                        "color": fill_color.name(),
                        "outline_color": (
                            stroke_color.name()
                            if stroke_color is not None
                            else fill_color.name()
                        ),
                        "outline_width": 0.26,
                    }
                )
                new_style.setSymbol(new_symbol)
        new_styles.append(new_style)
    new_renderer = QgsVectorTileBasicRenderer()
    new_renderer.setStyles(new_styles)
    layer.setRenderer(new_renderer)
    layer.triggerRepaint()


def adjust_legend(
    print_layout: QgsPrintLayout,
    color_entries: dict,
    colorbar_path: Path,
):
    legend = print_layout.itemById("legend")
    legend = cast(QgsLayoutItemPicture, legend)
    generate_colorbar(color_entries, colorbar_path)
    legend.setMode(Qgis.PictureFormat.SVG)
    legend.setPicturePath(path=str(colorbar_path), format=Qgis.PictureFormat.SVG)
    legend.setResizeMode(QgsLayoutItemPicture.ResizeMode.ZoomResizeFrame)
    legend.refreshPicture()


def reorder_layers(root: QgsLayerTree, layer_order: Iterable[QgsMapLayer]) -> None:
    for idx, map_layer in enumerate(layer_order):
        logger(f"reordering layer {idx=} {map_layer=}")
        layer_node = root.findLayer(map_layer.id())
        logger(f"layer_node {layer_node=}")
        cloned = layer_node.clone()
        logger(f"cloned {cloned=}")
        root.insertChildNode(idx, cloned)
        parent = layer_node.parent()
        logger(f"parent {parent=}")
        parent = cast(QgsLayerTreeGroup, parent)
        parent.removeChildNode(layer_node)
        cloned = None  # noqa
        del cloned


def refresh_layout_variables(
    print_layout: QgsLayout,
    layout_variables: Union[
        models.ForecastMapLayoutVariables, models.HistoricalMapLayoutVariables
    ],
) -> None:
    logger(f"{layout_variables=}")
    logger(f"{layout_variables.__dict__.items()=}")
    QgsExpressionContextUtils.setLayoutVariables(
        print_layout, {f"cline_{k}": v for k, v in layout_variables.__dict__.items()}
    )


def get_arpav_cline_details(
    url: str, network_access_manager: QgsNetworkAccessManager
) -> dict:
    backend_request = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
    reply_content = network_access_manager.blockingGet(backend_request)
    if reply_content.error() == QtNetwork.QNetworkReply.NetworkError.NoError:
        return json.loads(reply_content.content().data().decode("utf-8"))
    else:
        logger(reply_content.errorString())
        logger(reply_content.content().data().decode("utf-8"))
        raise ClinePrinterException("Not able to get arpav-cline details")


def load_cline_wms_layer(
    wms_base_url: str, layer_name: str, qgis_project: QgsProject
) -> QgsMapLayer:
    layer_load_params = {
        "crs": "EPSG:4326",
        "url": wms_base_url,
        "format": "image/png",
        "layers": layer_name,
        "styles": "",
        "version": "auto",
        "no_cache": str(uuid.uuid4()),
    }
    wms_layer = QgsRasterLayer(
        urllib.parse.unquote(urllib.parse.urlencode(layer_load_params)),
        layer_name,
        "wms",
    )
    logger(f"valid: {wms_layer.isValid()=}")
    return qgis_project.addMapLayer(wms_layer)


def load_cline_vector_tile_layer(
    layer_url_template: str, layer_name: str, qgis_project: QgsProject
) -> QgsMapLayer:
    vector_layer_params = {
        "type": "xyz",
        "url": layer_url_template,
    }
    vector_tile_layer = QgsVectorTileLayer(
        urllib.parse.unquote(
            urllib.parse.urlencode(vector_layer_params),
        ),
        layer_name,
    )
    logger(f"{vector_tile_layer.isValid()=}")
    return qgis_project.addMapLayer(vector_tile_layer)


def old_generate_colorbar(
    color_entries: dict,
    output_path: Path,
    orientation: Literal["horizontal", "vertical"] = "horizontal",
    title: str | None = None,
) -> None:
    values = [entry["value"] for entry in color_entries]
    colors = []
    for entry in color_entries:
        hex_color = entry["color"]
        alpha_hex = hex_color[1:3]
        rgb_hex = hex_color[3:]
        r = int(rgb_hex[0:2], 16) / 255
        g = int(rgb_hex[2:4], 16) / 255
        b = int(rgb_hex[4:6], 16) / 255
        alpha = int(alpha_hex, 16) / 255
        colors.append((r, g, b, alpha))

    # Create a custom colormap
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "custom_cmap",
        list(
            zip((np.array(values) - min(values)) / (max(values) - min(values)), colors)
        ),
    )

    if orientation == "horizontal":
        fig = plt.figure(figsize=(8, 2))
        gs = GridSpec(2, 1, height_ratios=[1, 3], hspace=0)
    else:
        fig = plt.figure(figsize=(2.5, 8))
        gs = GridSpec(2, 1, height_ratios=[1, 9], hspace=0)

    # Create title subplot (top)
    title_ax = fig.add_subplot(gs[0])
    title_ax.text(0.5, 0.3, title, ha="center", va="center", fontsize=12)
    title_ax.set_axis_off()

    # Create colorbar subplot (bottom)
    cbar_ax = fig.add_subplot(gs[1])
    cbar_ax.set_axis_off()

    # Create a subplot just for the colorbar inside the lower subplot
    if orientation == "horizontal":
        colorbar_only_ax = cbar_ax.inset_axes([0.05, 0.4, 0.9, 0.5])
    else:
        colorbar_only_ax = cbar_ax.inset_axes([0.3, 0.05, 0.4, 0.9])

    # Create a scalar mappable with the colormap
    norm = mcolors.Normalize(vmin=min(values), vmax=max(values))
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    # Create the colorbar
    if orientation == "horizontal":
        cbar = fig.colorbar(sm, cax=colorbar_only_ax, orientation="horizontal")
    else:
        cbar = fig.colorbar(sm, cax=colorbar_only_ax, orientation="vertical")
    cbar.set_ticks(values)
    cbar.set_ticklabels([str(val) for val in values])
    cbar.ax.tick_params(labelsize=8)

    plt.savefig(
        output_path, dpi=300, bbox_inches="tight", transparent=True, pad_inches=0.05
    )


def generate_colorbar(
    color_entries: dict,
    output_path: Path,
):
    values = [entry["value"] for entry in color_entries]
    colors = []
    for entry in color_entries:
        hex_color = entry["color"]
        alpha_hex = hex_color[1:3]  # ff in #ffxxxxxx
        rgb_hex = hex_color[3:]  # xxxxxx in #ffxxxxxx
        r = int(rgb_hex[0:2], 16) / 255
        g = int(rgb_hex[2:4], 16) / 255
        b = int(rgb_hex[4:6], 16) / 255
        alpha = int(alpha_hex, 16) / 255
        colors.append((r, g, b, alpha))

    cmap = mcolors.LinearSegmentedColormap.from_list(
        "custom_cmap",
        list(
            zip((np.array(values) - min(values)) / (max(values) - min(values)), colors)
        ),
    )

    fig = plt.figure(figsize=(1.5, 6))
    ax = plt.subplot(111)
    ax.set_axis_off()
    norm = mcolors.Normalize(vmin=min(values), vmax=max(values))
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, orientation="vertical", fraction=0.8, pad=0.2)
    cbar.set_ticks(values)
    cbar.set_ticklabels([str(val) for val in values])
    cbar.ax.tick_params(labelsize=8)

    # Save with minimal padding
    plt.savefig(
        output_path, dpi=300, transparent=True, bbox_inches="tight", pad_inches=0.05
    )
