from typing import Any
from ..utils.utils import parse_and_check_login

async def change_thread_emoji(post_func, ctx: Any, emoji: str, thread_id: str):
    form = {
        "emoji_choice": emoji,
        "thread_or_other_fbid": thread_id,
    }
    res = await post_func("https://www.facebook.com/messaging/save_thread_emoji/?source=thread_settings&__pc=EXP1%3Amessengerdotcom_pkg", ctx, form)
    res_data = parse_and_check_login(ctx, res)
    if not res_data: return None
    if res_data.get("error") == 1357031:
        raise Exception("Trying to change emoji of a chat that doesn't exist.")
    if res_data.get("error"):
        raise Exception(f"Error changing thread emoji: {res_data['error']}")
    return res_data
