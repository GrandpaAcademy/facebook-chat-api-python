from typing import Any
from ..utils.utils import parse_and_check_login


async def change_nickname(
    post_func, ctx: Any, nickname: str, thread_id: str, participant_id: str
):
    form = {
        "nickname": nickname,
        "participant_id": participant_id,
        "thread_or_other_fbid": thread_id,
    }
    res = await post_func(
        "https://www.facebook.com/messaging/save_thread_nickname/?source=thread_settings&dpr=1",
        ctx,
        form,
    )
    res_data = parse_and_check_login(ctx, res)
    if not res_data:
        return None
    if res_data.get("error") == 1545014:
        raise Exception("Trying to change nickname of user isn't in thread")
    if res_data.get("error") == 1357031:
        raise Exception(
            "Trying to change user nickname of a thread that doesn't exist."
        )
    if res_data.get("error"):
        raise Exception(f"Error changing nickname: {res_data['error']}")
    return res_data
