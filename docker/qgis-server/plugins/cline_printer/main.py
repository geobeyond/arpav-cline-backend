import json
import urllib.parse

from qgis.PyQt import (
    QtCore,
    QtNetwork,
)
from qgis.core import (
    QgsExpressionContextUtils,
    QgsLayout,
    QgsLayoutItemHtml,
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
                    self.layout_name, cov_details, wms_layer_name, project
                )
                wms_service_name = "WMS"
                wms_version = "1.3.0"
                request.setParameter("SERVICE", wms_service_name)
                request.setParameter("VERSION", wms_version)
                request.setParameter("REQUEST", "GetPrint")
                wms_service = self.server_iface.serviceRegistry().getService(
                    wms_service_name, wms_version
                )
                return wms_service.executeRequest(request, response, project)


def write_error(response: QgsServerResponse, message: str):
    response.write(json.dumps({"detail": message}))
    response.setHeader("Content-Type", "application/json")
    response.setStatusCode(400)
    response.finish()


def adjust_print_layout(
    layout_name, coverage_details: dict, wms_layer_name: str, qgis_project: QgsProject
) -> None:
    load_cline_wms_layer(coverage_details["wms_base_url"], wms_layer_name, qgis_project)
    load_cline_vector_tile_layer(
        coverage_details["observation_stations_vector_tile_layer_url"], qgis_project
    )
    layout_manager = qgis_project.layoutManager()
    print_layout = layout_manager.layoutByName(layout_name)
    refresh_layout_variables(print_layout, coverage_details)
    map_info_html_layout_element = print_layout.itemById("map_info").multiFrame()
    update_layout_item_html(map_info_html_layout_element, coverage_details)


def refresh_layout_variables(print_layout: QgsLayout, coverage_details: dict) -> None:
    QgsExpressionContextUtils.setLayoutVariable(
        print_layout,
        "arpav_title",
        coverage_details["display_name_english"],
    )


def update_layout_item_html(
    html_item: QgsLayoutItemHtml, coverage_details: dict
) -> None:
    map_info_html = "<table>"
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
    logger(f"{wms_layer.isValid()=}")
    return qgis_project.addMapLayer(wms_layer)


def load_cline_vector_tile_layer(
    layer_url_template: str, qgis_project: QgsProject
) -> QgsMapLayer:
    vector_layer_params = {
        "type": "xyz",
        "url": layer_url_template,
    }
    vector_tile_layer = QgsVectorTileLayer(
        urllib.parse.unquote(
            urllib.parse.urlencode(vector_layer_params),
        ),
        "observation stations",
    )
    logger(f"{vector_tile_layer.isValid()=}")
    return qgis_project.addMapLayer(vector_tile_layer)
