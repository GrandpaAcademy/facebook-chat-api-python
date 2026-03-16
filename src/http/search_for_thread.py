from typing import Any
from ..utils.utils import parse_and_check_login

async def search_for_thread(post_func, ctx: Any, name: str):
    form = {
        "client": "web_messenger",
        "query": name,
        "offset": 0,
        "limit": 21,
        "index": "fbid",
    }
    
    url = "https://www.facebook.com/ajax/mercury/search_threads.php"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)
    
    if res_data and res_data.get("error"):
        raise Exception(f"searchForThread error: {res_data['error']}")
        
    if not res_data or "payload" not in res_data or "mercury_payload" not in res_data["payload"] or "threads" not in res_data["payload"]["mercury_payload"]:
         raise Exception(f"Could not find thread `{name}`.")
         
    # Note: In a real implementation, we'd use a thread formatter here.
    # For now, we return the raw thread data from the payload.
    return res_data["payload"]["mercury_payload"]["threads"]
