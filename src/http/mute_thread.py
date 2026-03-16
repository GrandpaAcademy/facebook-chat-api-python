from typing import Any
from ..utils.utils import parse_and_check_login


async def mute_thread(post_func, ctx: Any, thread_id: str, mute_seconds: int):
    # mute_seconds: -1=permanent mute, 0=unmute, 60=one minute, 3600=one hour, etc.
    form = {"thread_fbid": thread_id, "mute_settings": mute_seconds}

    url = "https://www.facebook.com/ajax/mercury/change_mute_thread.php"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)

    if res_data and res_data.get("error"):
        raise Exception(f"muteThread error: {res_data['error']}")
    return res_data
