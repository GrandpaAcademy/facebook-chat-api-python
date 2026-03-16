import json
import time
from typing import Any
from ..utils.utils import get_signature_id, parse_and_check_login

async def set_active_status(post_func, ctx: Any, is_active: bool):
    form = {}
    sig = get_signature_id()
    form.update({
        "__aaid": "0",
        "__req": sig,
        "__hs": "20351.HYP:comet_pkg.2.1...0",
        "dpr": "1",
        "__ccg": "EXCELLENT",
        "__rev": ctx.revision,
        "__s": sig,
        "__hsi": "7552256848274926554",
        "__comet_req": "15",
        "lsd": ctx.fb_dtsg,
        "__spin_r": ctx.revision,
        "__spin_b": "trunk",
        "__spin_t": str(int(time.time())),
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "UpdatePresenceSettingsMutation",
        "variables": json.dumps({
            "input": {
                "online_policy": "ALLOWLIST",
                "web_allowlist": [],
                "web_visibility": is_active,
                "actor_id": str(ctx.user_id),
                "client_mutation_id": "1"
            }
        }),
        "server_timestamps": "true",
        "doc_id": "9444355898946246"
    })
    
    res = await post_func("https://www.facebook.com/api/graphql/", ctx, form)
    return parse_and_check_login(ctx, res)
