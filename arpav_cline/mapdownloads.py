import io
import logging
import typing

from httpx import Client
from playwright.sync_api import sync_playwright

from .config import ArpavPpcvSettings

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


def get_map_print(
    http_client: Client,
    coverage_identifier: str,
    output_format: typing.Literal["jpg", "png", "pdf"],
    settings: ArpavPpcvSettings,
    main_layer: str | None = None,
    language_code: str | None = None,
):
    params = {
        "service": "CLINE_PRINTER",
        "coverage_identifier": coverage_identifier,
        "wms_layer_name": None,
        "format": output_format,
    }
    if main_layer:
        params["wms_layer_name"] = main_layer
    if language_code:
        params["language_code"] = language_code
    with http_client.stream(
        "GET", f"{settings.print_server_base_url}/ogc/", params=params
    ) as response:
        yield response.headers
        for data in response.iter_raw():
            yield data
