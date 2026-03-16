import json
from typing import Any
from ..utils.utils import parse_and_check_login, get_guid

async def change_username(post_func, ctx: Any, username: str):
    variables = {
        "client_mutation_id": get_guid(),
        "family_device_id": "device_id_fetch_datr",
        "identity_ids": [ctx.user_id],
        "username": username,
        "interface": "FB_WEB"
    }
    
    form = {
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "useFXIMUpdateUsernameMutation",
        "variables": json.dumps(variables),
        "server_timestamps": True,
        "doc_id": "5737739449613305"
    }
    
    headers = {
        "Origin": "https://accountscenter.facebook.com",
        "Referer": f"https://accountscenter.facebook.com/profiles/{ctx.user_id}/username/?entrypoint=fb_account_center"
    }
    
    url = "https://accountscenter.facebook.com/api/graphql/"
    res = await ctx.client.post(url, data=form, headers={**ctx.client.headers, **headers})
    res_data = parse_and_check_login(ctx, res)
    
    if res_data and res_data.get("errors"):
        raise Exception(f"changeUsername errors: {res_data['errors']}")
        
    if res_data and "data" in res_data and res_data["data"].get("fxim_update_identity_username", {}).get("error"):
        raise Exception(f"changeUsername data error: {res_data['data']['fxim_update_identity_username']['error']}")
        
    return res_data
