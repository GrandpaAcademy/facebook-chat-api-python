import json
from typing import Any
from ..utils.utils import parse_and_check_login, get_signature_id

async def get_thread_theme(post_func, ctx: Any, theme_id: str):
    form = {
        "av": ctx.user_id,
        "__user": ctx.user_id,
        "__a": 1,
        "__req": get_signature_id(),
        "fb_dtsg": ctx.fb_dtsg,
        "jazoest": getattr(ctx, "ttstamp", ""),
        "lsd": ctx.fb_dtsg,
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "MWPThreadThemeProviderQuery",
        "variables": json.dumps({
            "id": str(theme_id)
        }),
        "server_timestamps": True,
        "doc_id": "9734829906576883"
    }

    url = "https://www.facebook.com/api/graphql/"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)
    
    if res_data and res_data.get("errors"):
        raise Exception(f"getThreadTheme errors: {res_data['errors']}")

    if res_data and "data" in res_data and "messenger_thread_theme" in res_data["data"]:
        theme_data = res_data["data"]["messenger_thread_theme"]
        return {
            "id": theme_data.get("id"),
            "name": theme_data.get("accessibility_label"),
            "description": theme_data.get("description"),
            "colors": theme_data.get("gradient_colors") or [theme_data.get("fallback_color")],
            "backgroundImage": theme_data.get("background_asset", {}).get("image", {}).get("uri") if theme_data.get("background_asset") else None
        }
    else:
        raise Exception("No theme data found")
