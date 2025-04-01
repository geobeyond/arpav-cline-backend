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
    QgsServerFilter,
    QgsServerInterface,
    QgsServerRequest,
    QgsServerResponse,
    QgsService,
)

logger = QgsMessageLog.logMessage


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
        if (
            cov_identifier := original_params.get("CLINE_COVERAGE_IDENTIFIER")
        ) is not None:
            wms_layer_name = original_params.get("CLINE_WMS_LAYER_NAME")
            cov_details = get_coverage_details(
                cov_identifier, self.network_access_manager
            )
            adjust_print_layout(self.layout_name, cov_details, wms_layer_name, project)
            wms_service_name = "WMS"
            wms_version = "1.3.0"
            request.setParameter("SERVICE", wms_service_name)
            request.setParameter("VERSION", wms_version)
            request.setParameter("REQUEST", "GetPrint")
            wms_service = self.server_iface.serviceRegistry().getService(
                wms_service_name, wms_version
            )
            return wms_service.executeRequest(request, response, project)


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
        # server_iface.registerFilter(
        #     ClinePrinterServerFilter(server_iface), priority=100
        # )


class ClinePrinterServerFilter(QgsServerFilter):
    network_access_manager: QgsNetworkAccessManager

    def __init__(self, server_iface: QgsServerInterface):
        super().__init__(server_iface)
        self.network_access_manager = QgsNetworkAccessManager().instance()

    def onRequestReady(self) -> bool:
        """Callback for when the request is ready to be processed.

        This is called when the request is ready: incoming URL and data have been
        parsed and before entering the core services (WMS, WFS etc.) switch, this is
        the point where you can manipulate the input and perform actions like:

        - authentication/authorization
        - redirects
        - add/remove certain parameters (typenames for example)
        - raise exceptions

        You could even substitute a core service completely by changing SERVICE
        parameter and hence bypassing the core service completely (not that this
        make much sense though).

        """
        # request should look like this:
        #
        # {url}?
        # (qgis-server standard params, like the current extent, etc.)
        # cline_coverage_identifier
        # cline_wms_layer_name
        # cline_base_layer_name
        QgsMessageLog.logMessage(f"{self.__class__.__name__} inside onRequestReady")
        iface = self.serverInterface()
        request = iface.requestHandler()
        request_params = request.parameterMap()
        QgsMessageLog.logMessage(f"{request_params=}")
        if request_params.get("REQUEST") == "GetPrint":
            QgsMessageLog.logMessage("Preparing cline layers...")
            prefix = "CLINE_"
            cov_identifier = request_params.get(f"{prefix}COVERAGE_IDENTIFIER")
            wms_layer_name = request_params.get(f"{prefix}WMS_LAYER_NAME")
            QgsMessageLog.logMessage(f"{cov_identifier=}")
            QgsMessageLog.logMessage(f"{wms_layer_name=}")
            if cov_identifier is not None:
                # 1. Call the backend API and retrieve information about the
                # coverage configuration to display:
                backend_request = QtNetwork.QNetworkRequest(
                    QtCore.QUrl(
                        f"http://webapp:5001/api/v2/coverages/coverages/{cov_identifier}"
                    )
                )
                reply_content = self.network_access_manager.blockingGet(backend_request)
                response_content = json.loads(
                    reply_content.content().data().decode("utf-8")
                )
                QgsMessageLog.logMessage(f"{response_content=}")
                wms_base_url = response_content["wms_base_url"]
                layer_load_params = {
                    "crs": "EPSG:4326",
                    "url": wms_base_url,
                    "format": "image/png",
                    "layers": wms_layer_name,
                    "styles": "",
                    "version": "auto",
                }
                wms_layer = QgsRasterLayer(
                    urllib.parse.unquote(urllib.parse.urlencode(layer_load_params)),
                    wms_layer_name,
                    "wms",
                )
                QgsMessageLog.logMessage(f"{wms_layer.isValid()=}")
                qgis_project = _get_current_project(iface.configFilePath())
                loaded_wms_layer = qgis_project.addMapLayer(wms_layer)  # noqa

                vector_layer_url_template = response_content[
                    "observation_stations_vector_tile_layer_url"
                ]
                vector_layer_params = {
                    "type": "xyz",
                    "url": vector_layer_url_template,
                }
                vector_tile_layer = QgsVectorTileLayer(
                    urllib.parse.unquote(
                        urllib.parse.urlencode(vector_layer_params),
                    ),
                    "observation stations",
                )
                QgsMessageLog.logMessage(f"{vector_tile_layer.isValid()=}")
                loaded_vector_tile_layer = qgis_project.addMapLayer(vector_tile_layer)  # noqa
                layout_manager = qgis_project.layoutManager()
                print_layout = layout_manager.layoutByName("arpav-cline-printer-layout")
                QgsExpressionContextUtils.setLayoutVariable(
                    print_layout,
                    "arpav_title",
                    response_content["display_name_english"],
                )
                map_info_html_layout_element = print_layout.itemById(
                    "map_info"
                ).multiFrame()
                map_info_html = "<table>"
                for possible_value in response_content["possible_values"]:
                    map_info_html += (
                        f"<tr>"
                        f"<th>{possible_value['configuration_parameter_name']}</th>"
                        f"<td>{possible_value['configuration_parameter_value']}</td>"
                        f"</tr>"
                    )
                map_info_html += "</table>"
                map_info_html_layout_element.setContentMode(
                    QgsLayoutItemHtml.ContentMode.ManualHtml
                )
                map_info_html_layout_element.setHtml(map_info_html)
                map_info_html_layout_element.loadHtml()

                # - base WMS URL
                # - WMS layer name
                # - palette for the legend
                # - URL for stations
                # 2. Add stations as a vector tile layer
                # 3. Add coverage as a WMS layer
                # 4. Render the correct date for the coverage
                # 5. Generate a PNG with the legend
        return True

    def onSendResponse(self) -> bool:
        """
        This is called whenever any partial output is flushed from response buffer
        (i.e to FCGI stdout if the fcgi server is used) and from there, to the client.
        This occurs when huge content is streamed (like WFS GetFeature). In this
        case onSendResponse() may be called multiple times.

        Note that if the response is not streamed, then onSendResponse() will not be
        called at all.

        In all case, the last (or unique) chunk will be sent to client after a call
        to onResponseComplete().

        Returning False will prevent flushing of data to the client. This is
        desirable when a plugin wants to collect all chunks from a response
        and examine or change the response in onResponseComplete().

        """
        QgsMessageLog.logMessage(f"{self.__class__.__name__} inside onSendResponse")
        return True

    def onResponseComplete(self) -> bool:
        """
        This is called once when core services (if hit) finish their process and the
        request is ready to be sent to the client. As discussed above, this method
        will be called before the last (or unique) chunk of data is sent to the
        client. For streaming services, multiple calls to onSendResponse() might
        have been called.

        onResponseComplete() is the ideal place to provide new services implementation
        (WPS or custom services) and to perform direct manipulation of the output
        coming from core services (for example to add a watermark
        upon a WMS image).

        Note that returning False will prevent the next plugins to execute
        onResponseComplete() but, in any case, prevent response to be sent
        to the client.
        """
        QgsMessageLog.logMessage(f"{self.__class__.__name__} inside onResponseComplete")
        request = self.serverInterface().requestHandler()
        params = request.parameterMap()
        if params.get("SERVICE", "").upper == "HELLO":
            request.clear()
            request.setResponseHeader("Content-Type", "text/plain")
            request.appendBody(b"Hello from ClinePrinter!")
        if params.get("TEST_NEW_PARAM", "") == "yo":
            QgsMessageLog.logMessage("Found the custom parameter in the params")
        return True


def _get_current_project(configuration_path: str) -> QgsProject:
    current_project = QgsProject.instance()
    current_project.read(configuration_path)
    return current_project


def get_coverage_details(
    coverage_identifier: str, network_access_manager: QgsNetworkAccessManager
) -> dict:
    backend_request = QtNetwork.QNetworkRequest(
        QtCore.QUrl(
            f"http://webapp:5001/api/v2/coverages/coverages/{coverage_identifier}"
        )
    )
    reply_content = network_access_manager.blockingGet(backend_request)
    return json.loads(reply_content.content().data().decode("utf-8"))


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
