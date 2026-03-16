from typing import Any, List, Union
from ..utils.utils import parse_and_check_login

async def get_avatar_user(ctx: Any, user_ids: Union[str, List[str]], size: Union[int, List[int]] = 1500):
    if not hasattr(ctx, "access_token") or not ctx.access_token:
        raise Exception("Access token is required for get_avatar_user. Use get_access() first.")
        
    if isinstance(size, (int, str)):
        height = width = int(size)
    elif isinstance(size, list):
        height = size[0]
        width = size[1] if len(size) > 1 else size[0]
    else:
        height = width = 1500
        
    if not isinstance(user_ids, list):
        user_ids = [user_ids]
        
    results = {}
    for user_id in user_ids:
        url = f"https://graph.facebook.com/{user_id}/picture?height={height}&width={width}&redirect=false&access_token={ctx.access_token}"
        res = await ctx.client.get(url)
        res_data = parse_and_check_login(ctx, res)
        
        if res_data and "data" in res_data:
            results[user_id] = res_data["data"].get("url")
            
    return results
