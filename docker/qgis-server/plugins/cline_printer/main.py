import json
import urllib.parse
from pathlib import Path
from typing import (
    Iterable,
    cast,
)

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.gridspec import GridSpec
import numpy as np

from qgis.PyQt import (
    QtCore,
    QtNetwork,
)
from qgis.core import (
    QgsExpressionContextUtils,
    QgsLayout,
    QgsLayoutItemHtml,
    QgsLayoutItemMap,
    QgsLayerTree,
    QgsLayerTreeGroup,
    QgsMapLayer,
    QgsMessageLog,
    QgsNetworkAccessManager,
    QgsProject,
    QgsRasterLayer,
    QgsVectorTileLayer,
)
from qgis.server import (
    QgsServerInterface,
    QgsServerRequest,
    QgsServerResponse,
    QgsService,
)

logger = QgsMessageLog.logMessage


class ClinePrinterException(Exception):
    ...


class ClinePrinterService(QgsService):
    server_iface: QgsServerInterface
    network_access_manager: QgsNetworkAccessManager
    layout_name = "arpav-cline-printer-layout"
    vector_tile_layer_name = "observation_stations"
    webapp_service_internal_base_url = "http://webapp:5001"
    osm_layer_name = "osm_standard"
    municipalities_layer_name = "municipalities"

    def __init__(self, server_iface: QgsServerInterface, *args, **kwargs):
        self.server_iface = server_iface
        self.network_access_manager = QgsNetworkAccessManager().instance()
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
        try:
            cov_identifier = original_params.get("CLINE_COVERAGE_IDENTIFIER")
            if cov_identifier is None:
                raise ClinePrinterException(
                    "Missing CLINE_COVERAGE_IDENTIFIER parameter"
                )
            wms_layer_name = original_params.get("CLINE_WMS_LAYER_NAME")
            if wms_layer_name is None:
                write_error(response, "Missing CLINE_WMS_LAYER_NAME parameter")
        except ClinePrinterException as err:
            write_error(response, str(err))
        else:
            try:
                cov_details = get_coverage_details(
                    cov_identifier, self.network_access_manager
                )
            except ClinePrinterException as err:
                write_error(response, str(err))
            else:
                adjust_print_layout(
                    layout_name=self.layout_name,
                    coverage_details=cov_details,
                    wms_layer_name=wms_layer_name,
                    vector_tile_layer_name=self.vector_tile_layer_name,
                    osm_layer_name=self.osm_layer_name,
                    municipalities_layer_name=self.municipalities_layer_name,
                    qgis_project=project,
                    internal_url_base=self.webapp_service_internal_base_url,
                )
                wms_service_name = "WMS"
                wms_version = "1.3.0"
                request.setParameter("SERVICE", wms_service_name)
                request.setParameter("VERSION", wms_version)
                request.setParameter("REQUEST", "GetPrint")
                request.setParameter("MAP0:EXTENT", "1102160,5561549,1582115,5983379")
                request.setParameter("MAP0:SCALE", "2513142")
                # request.setParameter(f"LAYERS", ','.join(layer_names))
                request.removeParameter("CLINE_COVERAGE_IDENTIFIER")
                request.removeParameter("CLINE_WMS_LAYER_NAME")
                request.removeParameter("MAP")
                logger(f"loaded layers: {project.mapLayers()=}")
                logger(f"modified request parameters: {request.parameters()=}")
                wms_service = self.server_iface.serviceRegistry().getService(
                    wms_service_name, wms_version
                )
                return wms_service.executeRequest(request, response, project)


def write_error(response: QgsServerResponse, message: str):
    response.write(json.dumps({"detail": message}))
    response.setHeader("Content-Type", "application/json")
    response.setStatusCode(400)
    response.finish()


def get_webapp_service_internal_url(public_url: str, internal_url_base: str) -> str:
    return "/".join(
        (internal_url_base, public_url.replace("://", "").partition("/")[-1])
    )


def adjust_print_layout(
    *,
    layout_name: str,
    coverage_details: dict,
    wms_layer_name: str,
    vector_tile_layer_name: str,
    osm_layer_name: str,
    municipalities_layer_name: str,
    qgis_project: QgsProject,
    internal_url_base: str,
) -> None:
    internal_wms_base_url = get_webapp_service_internal_url(
        coverage_details["wms_base_url"], internal_url_base
    )
    logger(f"{internal_wms_base_url=}")
    internal_vector_tile_layer_url = get_webapp_service_internal_url(
        coverage_details["observation_stations_vector_tile_layer_url"],
        internal_url_base,
    )
    logger(f"{internal_vector_tile_layer_url=}")
    wms_map_layer = load_cline_wms_layer(
        internal_wms_base_url, wms_layer_name, qgis_project
    )
    wms_map_layer.setOpacity(0.9)
    vector_tile_map_layer = load_cline_vector_tile_layer(
        internal_vector_tile_layer_url, vector_tile_layer_name, qgis_project
    )
    vector_tile_map_layer.setOpacity(1)
    osm_standard_map_layer = qgis_project.mapLayersByName(osm_layer_name)[0]
    municipalities_map_layer = qgis_project.mapLayersByName(municipalities_layer_name)[
        0
    ]
    municipalities_map_layer.setOpacity(0.7)
    layer_order = [
        vector_tile_map_layer,
        municipalities_map_layer,
        wms_map_layer,
        osm_standard_map_layer,
    ]
    layer_tree_root = qgis_project.layerTreeRoot()
    reorder_layers(layer_tree_root, layer_order)
    # logger(f"{layer_tree_root.findLayers()=}")
    # layer_tree_root.reorderGroupLayers(layer_order)

    layout_manager = qgis_project.layoutManager()
    print_layout = layout_manager.layoutByName(layout_name)
    map_item: QgsLayoutItemMap | None = print_layout.itemById("map1")
    if map_item is not None:
        map_item.setKeepLayerSet(False)
        map_item.refresh()
    refresh_layout_variables(print_layout, coverage_details)
    map_info_html_layout_element = print_layout.itemById("map_info").multiFrame()
    update_layout_item_html(map_info_html_layout_element, coverage_details)
    print_layout.refresh()


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


def refresh_layout_variables(print_layout: QgsLayout, coverage_details: dict) -> None:
    QgsExpressionContextUtils.setLayoutVariable(
        print_layout,
        "arpav_title",
        coverage_details["display_name_english"],
    )


def update_layout_item_html(
    html_item: QgsLayoutItemHtml, coverage_details: dict
) -> None:
    map_info_html = f"<h3>{coverage_details['display_name_english']}</h3>" f"<table>"
    for possible_value in coverage_details["possible_values"]:
        map_info_html += (
            f"<tr>"
            f"<th>{possible_value['configuration_parameter_name']}</th>"
            f"<td>{possible_value['configuration_parameter_value']}</td>"
            f"</tr>"
        )
    map_info_html += "</table>"
    html_item.setContentMode(QgsLayoutItemHtml.ContentMode.ManualHtml)
    html_item.setHtml(map_info_html)
    html_item.loadHtml()


class ClinePrinterServer:
    def __init__(self, server_iface: QgsServerInterface):
        service_registry = server_iface.serviceRegistry()
        printer_service = ClinePrinterService(server_iface)
        service_registry.registerService(printer_service)


def get_coverage_details(
    coverage_identifier: str, network_access_manager: QgsNetworkAccessManager
) -> dict:
    backend_request = QtNetwork.QNetworkRequest(
        QtCore.QUrl(
            f"http://webapp:5001/api/v2/coverages/coverages/{coverage_identifier}"
        )
    )
    reply_content = network_access_manager.blockingGet(backend_request)
    if reply_content.error() == QtNetwork.QNetworkReply.NetworkError.NoError:
        return json.loads(reply_content.content().data().decode("utf-8"))
    else:
        logger(reply_content.errorString())
        logger(reply_content.content().data().decode("utf-8"))
        raise ClinePrinterException("Not able to get coverage details")


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


def generate_colorbar(
    color_entries: dict,
    title: str,
    output_path: Path,
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

    fig = plt.figure(figsize=(8, 2))
    gs = GridSpec(2, 1, height_ratios=[1, 3], hspace=0)

    # Create title subplot (top)
    title_ax = fig.add_subplot(gs[0])
    title_ax.text(0.5, 0.3, title, ha="center", va="center", fontsize=12)
    title_ax.set_axis_off()

    # Create colorbar subplot (bottom)
    cbar_ax = fig.add_subplot(gs[1])
    cbar_ax.set_axis_off()

    # Create a subplot just for the colorbar inside the lower subplot
    colorbar_only_ax = cbar_ax.inset_axes([0.05, 0.4, 0.9, 0.5])

    # Create a scalar mappable with the colormap
    norm = mcolors.Normalize(vmin=min(values), vmax=max(values))
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    # Create the colorbar
    cbar = fig.colorbar(sm, cax=colorbar_only_ax, orientation="horizontal")
    cbar.set_ticks(values)
    cbar.set_ticklabels([str(val) for val in values])
    cbar.ax.tick_params(labelsize=8)

    plt.savefig(
        output_path, dpi=300, bbox_inches="tight", transparent=True, pad_inches=0.05
    )
