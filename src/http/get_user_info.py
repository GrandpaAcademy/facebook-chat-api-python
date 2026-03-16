import json
import re
from typing import Any, List
from ..utils.utils import get_from

async def get_user_info(post_func, ctx: Any, ids: List[str]):
    form = {}
    for i, user_id in enumerate(ids):
        form[f"ids[{i}]"] = user_id
    res = await post_func("https://www.facebook.com/chat/user_info/", ctx, form)
    body = res.text
    body = re.sub(r'for\s*\(\s*;\s*;\s*\)\s*;\s*', '', body)
    if not body:
        raise Exception("Facebook returned an empty response body.")
    res_data = json.loads(body)
    if isinstance(res_data, list):
        res_data = res_data[0]
    if res_data.get("error"):
        raise Exception(res_data)
    profiles = {}
    if "payload" in res_data and "profiles" in res_data["payload"]:
        data = res_data["payload"]["profiles"]
        for user_id, user_data in data.items():
            profiles[user_id] = {
                "name": user_data.get("name", "Unknown"),
                "firstName": user_data.get("firstName", "Unknown"),
                "vanity": user_data.get("vanity", ""),
                "thumbSrc": user_data.get("thumbSrc", ""),
                "profileUrl": user_data.get("uri", f"https://www.facebook.com/{user_id}"),
                "gender": user_data.get("gender", ""),
                "type": user_data.get("type", "user"),
                "isFriend": user_data.get("is_friend", False),
                "isBirthday": user_data.get("is_birthday", False)
            }
    return profiles
