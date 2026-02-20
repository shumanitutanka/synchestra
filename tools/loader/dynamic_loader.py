# synchestra/tools/loader/dynamic_loader.py

import asyncio
import hashlib
import time
from datetime import datetime
from playwright.async_api import async_playwright

class DynamicLoaderError(Exception):
    pass

def _hash_url(url):
    return hashlib.sha256(url.encode()).hexdigest()[:6]

async def load_dynamic_async(
    url,
    selector=None,
    timeout_load=8000,
    timeout_selector=5000,
    timeout_fallback=2000,
    user_agent=None,
    viewport=None,
    cookies=None,
    screenshot="none",
    js_enabled=True
):
    start = time.time()

    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)

            context = await browser.new_context(
                user_agent=user_agent or (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/121.0 Safari/537.36"
                ),
                viewport=viewport or {"width": 1280, "height": 2000},
                java_script_enabled=js_enabled
            )

            if cookies:
                await context.add_cookies(cookies)

            page = await context.new_page()

            # STEP 1 — load event
            await page.goto(url, wait_until="load", timeout=timeout_load)

            selector_found = None

            # STEP 2 — wait for selector (if provided)
            if selector:
                try:
                    await page.wait_for_selector(selector, timeout=timeout_selector)
                    selector_found = True
                except Exception:
                    selector_found = False

            # STEP 3 — fallback wait
            await page.wait_for_timeout(timeout_fallback)

            # Extract HTML
            html = await page.content()

            # Screenshot
            screenshot_path = None
            screenshot_base64 = None

            if screenshot == "file":
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                h = _hash_url(url)
                screenshot_path = f"screenshot_{ts}_{h}.png"
                await page.screenshot(path=screenshot_path, full_page=True)

            elif screenshot == "base64":
                screenshot_base64 = await page.screenshot(encoding="base64", full_page=True)

            await browser.close()

    except Exception as e:
        raise DynamicLoaderError(f"Dynamic loader failed: {e}")

    elapsed = int((time.time() - start) * 1000)

    meta = {
        "url_final": url,
        "status": 200,
        "mode_used": "dynamic",
        "load_time_ms": elapsed,
        "selector_used": selector,
        "selector_found": selector_found,
        "screenshot_path": screenshot_path,
        "screenshot_base64": screenshot_base64,
        "error": None
    }

    return html, meta


def load_dynamic(**kwargs):
    return asyncio.run(load_dynamic_async(**kwargs))
