import json
import time
from typing import Any, Optional
from ..utils.utils import parse_and_check_login, get_signature_id

async def suggest_friend(post_func, ctx: Any, count: int = 30, cursor: Optional[str] = None):
    form = {
        "av": ctx.user_id,
        "__aaid": 0,
        "__user": ctx.user_id,
        "__a": 1,
        "__req": get_signature_id(),
        "__hs": "20405.HYP:comet_pkg.2.1...0",
        "dpr": 1,
        "__ccg": "EXCELLENT",
        "__rev": "1029835515",
        "__s": get_signature_id(),
        "__hsi": int(time.time() * 1000),
        "__comet_req": 15,
        "fb_dtsg": ctx.fb_dtsg,
        "jazoest": getattr(ctx, "ttstamp", ""),
        "lsd": ctx.fb_dtsg,
        "__spin_r": "1029835515",
        "__spin_b": "trunk",
        "__spin_t": int(time.time() * 1000),
        "__crn": "comet.fbweb.CometPYMKSuggestionsRoute",
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "FriendingCometPYMKPanelPaginationQuery",
        "server_timestamps": True,
        "variables": json.dumps({
            "count": count,
            "cursor": cursor,
            "location": "FRIENDS_HOME_MAIN",
            "scale": 3
        }),
        "doc_id": "9917809191634193"
    }

    url = "https://www.facebook.com/api/graphql/"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)
    
    if res_data and res_data.get("errors"):
        raise Exception(f"suggestFriend errors: {res_data['errors']}")

    if res_data and "data" in res_data and "viewer" in res_data["data"] and res_data["data"]["viewer"].get("people_you_may_know"):
        pymk_data = res_data["data"]["viewer"]["people_you_may_know"]
        suggestions = []
        for edge in pymk_data.get("edges", []):
            node = edge.get("node", {})
            suggestions.append({
                "id": node.get("id"),
                "name": node.get("name"),
                "url": node.get("url"),
                "friendshipStatus": node.get("friendship_status"),
                "profilePicture": node.get("profile_picture", {}).get("uri") if node.get("profile_picture") else None,
                "mutualFriends": node.get("social_context", {}).get("text", ""),
                "topMutualFriends": node.get("social_context_top_mutual_friends", [])
            })

        return {
            "suggestions": suggestions,
            "hasNextPage": pymk_data.get("page_info", {}).get("has_next_page"),
            "endCursor": pymk_data.get("page_info", {}).get("end_cursor")
        }
    else:
        raise Exception("Invalid response format")
