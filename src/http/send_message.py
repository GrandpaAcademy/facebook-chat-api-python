import time
from typing import Any, Optional, Dict
from ..utils.utils import generate_offline_threading_id, generate_threading_id

async def send_message(post_func, ctx: Any, msg: Any, thread_id: str, is_single_user: Optional[bool] = None, reply_to_message: Optional[str] = None):
    if isinstance(msg, str):
        msg = {"body": msg}
    message_and_otid = generate_offline_threading_id()
    form = {
        "client": "mercury",
        "action_type": "ma-type:user-generated-message",
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
        "body": msg.get("body", ""),
        "offline_threading_id": message_and_otid,
        "message_id": message_and_otid,
        "threading_id": generate_threading_id(ctx.client_id),
    }
    if reply_to_message:
        form["replied_to_message_id"] = reply_to_message
    if is_single_user:
        form["specific_to_list[0]"] = f"fbid:{thread_id}"
        form["specific_to_list[1]"] = f"fbid:{ctx.user_id}"
        form["other_user_fbid"] = thread_id
    else:
        form["thread_fbid"] = thread_id
    
    res = await post_func("https://www.facebook.com/messaging/send/", ctx, form)
    return res.json()
