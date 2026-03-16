from typing import Any, Optional
from ..utils.utils import parse_and_check_login


async def send_typing_indicator(
    post_func,
    get_user_info_func,
    ctx: Any,
    thread_id: str,
    is_typing: bool,
    is_group: Optional[bool] = None,
):
    async def make_typing_indicator(typ: bool, t_id: str, group: Optional[bool]):
        form = {
            "typ": 1 if typ else 0,
            "to": "",
            "source": "mercury-chat",
            "thread": t_id,
        }

        if group is True:
            pass  # form.to remains empty for groups? original code: if (!isGroup) { form.to = threadID; }
        elif group is False:
            form["to"] = t_id
        else:
            # Auto detect
            user_info = await get_user_info_func(t_id)
            if user_info and len(user_info) > 0:
                form["to"] = t_id

        res = await post_func(
            "https://www.facebook.com/ajax/messaging/typ.php", ctx, form
        )
        res_data = parse_and_check_login(ctx, res)
        if res_data and res_data.get("error"):
            raise Exception(f"Typing indicator error: {res_data['error']}")
        return res_data

    await make_typing_indicator(is_typing, thread_id, is_group)

    # Return a closer function to stop typing
    async def stop():
        await make_typing_indicator(False, thread_id, is_group)

    return stop
