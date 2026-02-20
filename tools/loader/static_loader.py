# synchestra/tools/loader/static_loader.py

import requests
import time

class StaticLoaderError(Exception):
    pass

def load_static(url, user_agent=None, timeout=8000):
    start = time.time()

    headers = {
        "User-Agent": user_agent or (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/121.0 Safari/537.36"
        )
    }

    try:
        r = requests.get(url, headers=headers, timeout=timeout/1000)
    except Exception as e:
        raise StaticLoaderError(f"Static request failed: {e}")

    if r.status_code != 200:
        raise StaticLoaderError(f"Static loader got HTTP {r.status_code}")

    html = r.text
    elapsed = int((time.time() - start) * 1000)

    meta = {
        "url_final": r.url,
        "status": r.status_code,
        "mode_used": "static",
        "load_time_ms": elapsed,
        "selector_used": None,
        "selector_found": None,
        "screenshot_path": None,
        "screenshot_base64": None,
        "error": None
    }

    return html, meta
