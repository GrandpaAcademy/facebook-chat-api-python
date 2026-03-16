from typing import Any
from ..utils.utils import parse_and_check_login


async def unfriend(post_func, ctx: Any, user_id: str):
    form = {
        "uid": str(user_id),
        "unref": "bd_friends_tab",
        "floc": "friends_tab",
        "nctr[_mod]": f"pagelet_timeline_app_collection_{ctx.user_id}:2356318349:2",
    }

    url = "https://www.facebook.com/ajax/profile/removefriendconfirm.php"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)

    if res_data and res_data.get("error"):
        raise Exception(f"unfriend error: {res_data['error']}")

    return res_data
