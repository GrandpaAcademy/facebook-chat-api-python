from typing import Any, List, Union
from ..utils.utils import parse_and_check_login

async def delete_thread(post_func, ctx: Any, thread_or_threads: Union[str, List[str]]):
    form = {
        "client": "mercury",
    }
    
    if not isinstance(thread_or_threads, list):
        thread_or_threads = [thread_or_threads]
        
    for i, thread_id in enumerate(thread_or_threads):
        form[f"ids[{i}]"] = thread_id
        
    url = "https://www.facebook.com/ajax/mercury/delete_thread.php"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)
    
    if res_data and res_data.get("error"):
        raise Exception(f"deleteThread error: {res_data['error']}")
    return res_data
