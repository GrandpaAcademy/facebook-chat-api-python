import time
from typing import Any
from ..utils.utils import parse_and_check_login


async def mark_as_read(post_func, ctx: Any, thread_id: str, read: bool = True):
    form = {
        "ids[" + thread_id + "]": "true" if read else "false",
        "watermarkTimestamp": int(time.time() * 1000),
        "shouldSendReadReceipt": "true",
        "commerce_last_message_type": "",
    }
    res = await post_func(
        "https://www.facebook.com/ajax/mercury/change_read_status.php", ctx, form
    )
    return parse_and_check_login(ctx, res)
