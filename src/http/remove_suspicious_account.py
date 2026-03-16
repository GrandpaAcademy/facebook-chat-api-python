from typing import Any
from ..utils.utils import (
    post,
    parse_and_check_login,
    get_guid,
    get_event_time,
    get_jazoest,
    get_session_id,
)


async def remove_suspicious_account(ctx: Any):
    form = {
        "av": ctx.user_id,
        "__user": ctx.user_id,
        "__a": "1",
        "__req": get_guid(),
        "__hs": get_event_time(),
        "dpr": "1",
        "__ccg": "EXCELLENT",
        "__rev": "1029700657",
        "__s": get_session_id(),
        "__hsi": get_event_time(),
        "__dyn": "",
        "__csr": "",
        "__comet_req": "15",
        "fb_dtsg": ctx.fb_dtsg or "",
        "jazoest": get_jazoest(ctx.fb_dtsg),
        "__spin_r": "1029700657",
        "__spin_b": "trunk",
        "__spin_t": get_event_time(),
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "FBScrapingWarningMutation",
        "server_timestamps": "true",
        "variables": "{}",
        "doc_id": "24406519995698862",
    }

    res = await post("https://www.facebook.com/api/graphql/", ctx, form)
    res_data = parse_and_check_login(ctx)(res)

    if res_data.get("error"):
        raise Exception(f"removeSuspiciousAccount error: {res_data.get('error')}")

    return {"success": True, "message": "Suspicious account warning removed"}
