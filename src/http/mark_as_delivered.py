from typing import Any
from ..utils.utils import parse_and_check_login

async def mark_as_delivered(post_func, ctx: Any, thread_id: str, message_id: str):
    form = {}
    form["message_ids[0]"] = message_id
    form[f"thread_ids[{thread_id}][0]"] = message_id
    
    res = await post_func("https://www.facebook.com/ajax/mercury/delivery_receipts.php", ctx, form)
    # Node.js implementation doesn't strictly parse results but checks for errors
    res_data = parse_and_check_login(ctx, res)
    if res_data and res_data.get("error"):
        raise Exception(f"markAsDelivered error: {res_data['error']}")
    return res_data
