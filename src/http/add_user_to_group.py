import time
from typing import Any, List, Union
from ..utils.utils import (
    parse_and_check_login, 
    generate_offline_threading_id, 
    generate_timestamp_relative,
    generate_threading_id
)

async def add_user_to_group(post_func, ctx: Any, user_ids: Union[str, List[str]], thread_id: str):
    if isinstance(user_ids, str):
        user_ids = [user_ids]
        
    otid = generate_offline_threading_id()
    form = {
        "client": "mercury",
        "action_type": "ma-type:log-message",
        "author": f"fbid:{ctx.user_id}",
        "thread_id": "",
        "timestamp": int(time.time() * 1000),
        "timestamp_absolute": "Today",
        "timestamp_relative": generate_timestamp_relative(),
        "timestamp_time_passed": "0",
        "is_unread": False,
        "is_cleared": False,
        "is_forward": False,
        "is_filtered_content": False,
        "is_filtered_content_bh": False,
        "is_filtered_content_account": False,
        "is_spoof_warning": False,
        "source": "source:chat:web",
        "source_tags[0]": "source:chat",
        "log_message_type": "log:subscribe",
        "status": "0",
        "offline_threading_id": otid,
        "message_id": otid,
        "threading_id": generate_threading_id(ctx.client_id),
        "manual_retry_cnt": "0",
        "thread_fbid": thread_id,
    }
    
    for i, user_id in enumerate(user_ids):
        form[f"log_message_data[added_participants][{i}]"] = f"fbid:{user_id}"
        
    res = await post_func("https://www.facebook.com/messaging/send/", ctx, form)
    res_data = parse_and_check_login(ctx, res)
    if not res_data:
        raise Exception("Add to group failed.")
    if res_data.get("error"):
        raise Exception(f"Error adding to group: {res_data['error']}")
    return res_data
