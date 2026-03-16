from typing import Any
from ..utils.utils import parse_and_check_login


async def unsend_message(post_func, ctx: Any, message_id: str):
    form = {"message_id": message_id}
    res = await post_func(
        "https://www.facebook.com/messaging/unsend_message/", ctx, form
    )
    return parse_and_check_login(ctx, res)
