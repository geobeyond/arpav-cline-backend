import json
import urllib.parse

from qgis.PyQt import (
    QtCore,
    QtNetwork,
)
from qgis.core import (
    QgsMessageLog,
    QgsNetworkAccessManager,
    QgsProject,
    QgsRasterLayer,
)
from qgis.server import (
    QgsServerFilter,
    QgsServerInterface,
)


class ClinePrinterServer:
    def __init__(self, server_iface: QgsServerInterface):
        server_iface.registerFilter(
            ClinePrinterServerFilter(server_iface), priority=100
        )


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
        # arpav_cline_coverage_identifier
        # arpav_cline_wms_layer_name
        # arpav_cline_base_layer_name
        QgsMessageLog.logMessage(f"{self.__class__.__name__} inside onRequestReady")
        request = self.serverInterface().requestHandler()
        request_params = request.parameterMap()
        if request_params.get("request") == "GetPrint":
            prefix = "cline_"
            cov_identifier = request_params.get(f"{prefix}cov_identifier")
            wms_layer_name = request_params.get(f"{prefix}wms_layer_name")
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
                loaded_layer = QgsProject.instance().addMapLayer(wms_layer)  # noqa

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
