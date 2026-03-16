import time
from typing import Any
from ..utils.utils import (
    generate_offline_threading_id,
    generate_threading_id,
    parse_and_check_login,
)


async def set_title(post_func, ctx: Any, new_title: str, thread_id: str):
    message_and_otid = generate_offline_threading_id()
    form = {
        "client": "mercury",
        "action_type": "ma-type:log-message",
        "author": f"fbid:{ctx.user_id}",
        "timestamp": int(time.time() * 1000),
        "timestamp_absolute": "Today",
        "timestamp_relative": "Now",
        "timestamp_time_passed": "0",
        "is_unread": "false",
        "is_cleared": "false",
        "is_forward": "false",
        "is_filtered_content": "false",
        "source": "source:chat:web",
        "offline_threading_id": message_and_otid,
        "message_id": message_and_otid,
        "threading_id": generate_threading_id(ctx.client_id),
        "thread_fbid": thread_id,
        "thread_name": new_title,
        "thread_id": thread_id,
        "log_message_type": "log:thread-name",
    }
    res = await post_func(
        "https://www.facebook.com/messaging/set_thread_name/", ctx, form
    )
    return parse_and_check_login(ctx, res)
