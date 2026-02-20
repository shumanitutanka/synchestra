# synchestra/tools/loader/universal_loader.py

from .static_loader import load_static, StaticLoaderError
from .dynamic_loader import load_dynamic, DynamicLoaderError

class UniversalLoaderError(Exception):
    pass

def load_page(
    url,
    mode="auto",
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
    # MANUAL STATIC
    if mode == "static":
        return load_static(url, user_agent=user_agent, timeout=timeout_load)

    # MANUAL DYNAMIC
    if mode == "dynamic":
        return load_dynamic(
            url=url,
            selector=selector,
            timeout_load=timeout_load,
            timeout_selector=timeout_selector,
            timeout_fallback=timeout_fallback,
            user_agent=user_agent,
            viewport=viewport,
            cookies=cookies,
            screenshot=screenshot,
            js_enabled=js_enabled
        )

    # AUTO MODE
    if mode == "auto":
        # Try static first
        try:
            html, meta = load_static(url, user_agent=user_agent, timeout=timeout_load)
            return html, meta
        except StaticLoaderError:
            pass

        # Fallback to dynamic
        try:
            return load_dynamic(
                url=url,
                selector=selector,
                timeout_load=timeout_load,
                timeout_selector=timeout_selector,
                timeout_fallback=timeout_fallback,
                user_agent=user_agent,
                viewport=viewport,
                cookies=cookies,
                screenshot=screenshot,
                js_enabled=js_enabled
            )
        except DynamicLoaderError as e:
            raise UniversalLoaderError(f"Both static and dynamic loaders failed: {e}")

    raise UniversalLoaderError(f"Invalid mode: {mode}")
