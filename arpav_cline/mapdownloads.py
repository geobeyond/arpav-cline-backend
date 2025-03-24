import io
import logging

from httpx import Client
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


def grab_frontend_screenshot(
    url: str,
    frontend_settle_delay_seconds: int,
    load_timeout_seconds: int = 30,
) -> io.BytesIO:
    with sync_playwright() as playwright:
        device_profile = playwright.devices["Desktop Chrome HiDPI"]
        browser = playwright.chromium.launch()
        context = browser.new_context(
            **device_profile, locale="it-IT", timezone_id="Europe/Rome"
        )
        page = context.new_page()
        page.on("request", lambda request: logger.debug(f"{request=}"))
        page.on("response", lambda response: logger.debug(f"{response=}"))
        page.on(
            "console",
            lambda message: logger.debug(f"Console {message.type}: {message.text}"),
        )
        page.on(
            "response",
            lambda response: logger.debug(
                f"CSP headers: {response.headers.get('content-security-policy', 'None')}"
            ),
        )

        page.goto(
            url,
            wait_until="networkidle",
            timeout=load_timeout_seconds * 1000,
        )
        page.wait_for_timeout(frontend_settle_delay_seconds * 1000)
        screenshot_buffer = io.BytesIO(page.screenshot(type="png"))
        browser.close()
        screenshot_buffer.seek(0)
    return screenshot_buffer


def get_map_print(http_client: Client):
    response = http_client.get(  # noqa
        "http://qgis-server/ogc/",
        params={
            "service": "WMS",
            "request": "GetPrint",
            "template": "arpav-cline-printer-layout",
            "crs": "EPSG:3857",
            "cline_coverage_identifier": None,
            "cline_wms_layer_name": None,
        },
    )
