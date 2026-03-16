from typing import Any, List, Union
from ..utils.utils import parse_and_check_login

async def delete_message(post_func, ctx: Any, message_ids: Union[str, List[str]]):
    if isinstance(message_ids, str):
        message_ids = [message_ids]
    
    form = {"client": "mercury"}
    for i, msg_id in enumerate(message_ids):
        form[f"message_ids[{i}]"] = msg_id
        
    res = await post_func("https://www.facebook.com/ajax/mercury/delete_messages.php", ctx, form)
    return parse_and_check_login(ctx, res)
