import time
from typing import Any, Optional
from ..utils.utils import parse_and_check_login

async def mark_as_seen(post_func, ctx: Any, seen_timestamp: Optional[int] = None):
    if seen_timestamp is None:
        seen_timestamp = int(time.time() * 1000)
        
    form = {
        "seen_timestamp": seen_timestamp
    }
    
    url = "https://www.facebook.com/ajax/mercury/mark_seen.php"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)
    
    if res_data and res_data.get("error"):
        raise Exception(f"markAsSeen error: {res_data['error']}")
        
    return res_data
