from typing import Any
from ..utils.utils import parse_and_check_login

async def handle_friend_request(post_func, ctx: Any, user_id: str, accept: bool):
    form = {
        "viewer_id": ctx.user_id,
        "frefs[0]": "jwl",
        "floc": "friend_center_requests",
        "ref": "/reqs.php",
        "action": "confirm" if accept else "reject"
    }
    
    url = "https://www.facebook.com/requests/friends/ajax/"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)
    
    if res_data and "payload" in res_data and res_data["payload"].get("err"):
        raise Exception(f"handleFriendRequest error: {res_data['payload']['err']}")
        
    return res_data
