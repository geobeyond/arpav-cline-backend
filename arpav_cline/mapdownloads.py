import io

from playwright.sync_api import sync_playwright


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
        page.goto(url, timeout=load_timeout_seconds * 1000)
        page.wait_for_timeout(frontend_settle_delay_seconds * 1000)
        screenshot_buffer = io.BytesIO(page.screenshot(type="png"))
        browser.close()
        screenshot_buffer.seek(0)
    return screenshot_buffer
