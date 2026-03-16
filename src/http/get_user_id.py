from typing import Any
from ..utils.utils import parse_and_check_login, get_guid


def format_data(data: Any):
    return {
        "userID": str(data.get("uid")),
        "photoUrl": data.get("photo"),
        "indexRank": data.get("index_rank"),
        "name": data.get("text"),
        "isVerified": data.get("is_verified"),
        "profileUrl": data.get("path"),
        "category": data.get("category"),
        "score": data.get("score"),
        "type": data.get("type"),
    }


async def get_user_id(get_func, ctx: Any, name: str):
    form = {
        "value": name.lower(),
        "viewer": ctx.user_id,
        "rsp": "search",
        "context": "search",
        "path": "/home.php",
        "request_id": get_guid(),
    }

    res = await get_func(
        "https://www.facebook.com/ajax/typeahead/search.php", ctx, form
    )
    res_data = parse_and_check_login(ctx, res)
    if not res_data:
        return []
    if res_data.get("error"):
        raise Exception(f"getUserID error: {res_data['error']}")

    entries = res_data.get("payload", {}).get("entries", [])
    return [format_data(e) for e in entries]
