import json
import time
from typing import Any
from ..utils.utils import parse_and_check_login, get_guid

async def set_profile_lock(post_func, ctx: Any, enable: bool):
    form = {
        "av": ctx.user_id,
        "__aaid": 0,
        "__user": ctx.user_id,
        "__a": 1,
        "__req": get_guid(),
        "__hs": getattr(ctx, "fb_dtsg_ag", ""),
        "dpr": 1,
        "__ccg": "EXCELLENT",
        "__rev": getattr(ctx, "req_id", ""),
        "__s": get_guid(),
        "__hsi": getattr(ctx, "hsi", ""),
        "__comet_req": 15,
        "fb_dtsg": ctx.fb_dtsg,
        "jazoest": getattr(ctx, "ttstamp", ""),
        "lsd": ctx.fb_dtsg,
        "__spin_r": getattr(ctx, "req_id", ""),
        "__spin_b": "trunk",
        "__spin_t": int(time.time() * 1000),
        "__crn": "comet.fbweb.CometProfileTimelineListViewRoute",
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "WemPrivateSharingMutation",
        "server_timestamps": True,
        "variables": json.dumps({
            "enable": not enable
        }),
        "doc_id": "9144138075685633"
    }

    url = "https://www.facebook.com/api/graphql/"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)
    
    if res_data and res_data.get("errors"):
        raise Exception(f"setProfileLock errors: {res_data['errors']}")
        
    result = res_data.get("data", {}).get("toggle_wem_private_sharing_control_enabled")
    if not result:
        raise Exception("Cannot toggle profile lock status")
        
    return {
        "private_sharing_enabled": result.get("private_sharing_enabled"),
        "is_ppg_converter": result.get("is_ppg_converter"),
        "is_ppg_user": result.get("is_ppg_user"),
        "last_toggle_time": result.get("private_sharing_last_toggle_time"),
        "owner_id": result.get("owner_id")
    }
