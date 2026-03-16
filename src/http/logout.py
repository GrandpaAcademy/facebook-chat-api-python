import json
from typing import Any
from ..utils.utils import get_from, parse_and_check_login

async def logout(post_func, ctx: Any):
    menu_url = "https://www.facebook.com/bluebar/modern_settings_menu/?help_type=364455653583099&show_contextual_help=1"
    res = await post_func(menu_url, ctx, {"pmid": "0"})
    res_data = parse_and_check_login(ctx, res)
    if not res_data or "jsmods" not in res_data:
        raise Exception("Failed to get logout menu data")
    markup = json.dumps(res_data["jsmods"].get("markup", []))
    fb_dtsg = get_from(markup, 'fb_dtsg\\\\" value=\\\\"', '\\\\"')
    h = get_from(markup, 'h\\\\" value=\\\\"', '\\\\"')
    ref = get_from(markup, 'ref\\\\" value=\\\\"', '\\\\"')
    logout_form = {"fb_dtsg": fb_dtsg, "h": h, "ref": ref}
    await post_func("https://www.facebook.com/logout.php", ctx, logout_form)
    ctx.logged_in = False
    return True
