from typing import Any
from ..utils.utils import parse_and_check_login

async def remove_user_from_group(post_func, ctx: Any, user_id: str, thread_id: str):
    form = {
        "uid": user_id,
        "tid": thread_id,
    }
    res = await post_func("https://www.facebook.com/chat/remove_participants", ctx, form)
    res_data = parse_and_check_login(ctx, res)
    if not res_data:
        raise Exception("Remove from group failed.")
    if res_data.get("error"):
        raise Exception(f"Error removing from group: {res_data['error']}")
    return res_data
