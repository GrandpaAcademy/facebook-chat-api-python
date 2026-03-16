from typing import Any, Union, List
from ..utils.utils import parse_and_check_login

async def handle_message_request(post_func, ctx: Any, thread_id: Union[str, List[str]], accept: bool):
    if not isinstance(thread_id, list):
        thread_id = [thread_id]
        
    message_box = "inbox" if accept else "other"
    form = {
        "client": "mercury",
    }
    
    for i, t_id in enumerate(thread_id):
        form[f"{message_box}[{i}]"] = t_id
        
    url = "https://www.facebook.com/ajax/mercury/move_thread.php"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)
    
    if res_data and res_data.get("error"):
        raise Exception(f"handleMessageRequest error: {res_data['error']}")
        
    return res_data
