import io

from playwright.sync_api import sync_playwright


def grab_frontend_screenshot(url: str, delay_seconds: int) -> io.BytesIO:
    with sync_playwright() as playwright:
        device_profile = playwright.devices["Desktop Chrome HiDPI"]
        browser = playwright.chromium.launch()
        context = browser.new_context(**device_profile)
        page = context.new_page()
        page.goto(url)
        page.wait_for_timeout(delay_seconds * 1000)
        screenshot_buffer = io.BytesIO(page.screenshot(type="png"))
        browser.close()
        screenshot_buffer.seek(0)
    return screenshot_buffer
