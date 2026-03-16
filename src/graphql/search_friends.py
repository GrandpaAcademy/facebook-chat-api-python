import json
import time
from typing import Any
from ..utils.utils import parse_and_check_login, get_signature_id


async def search_friends(post_func, ctx: Any, search_query: str):
    form = {
        "av": ctx.user_id,
        "__aaid": 0,
        "__user": ctx.user_id,
        "__a": 1,
        "__req": get_signature_id(),
        "__hs": "20358.HYP:comet_pkg.2.1...0",
        "dpr": 1,
        "__ccg": "EXCELLENT",
        "__rev": "1027694919",
        "__s": get_signature_id(),
        "__hsi": "7554748243252799467",
        "__comet_req": 15,
        "fb_dtsg": ctx.fb_dtsg,
        "jazoest": getattr(ctx, "ttstamp", ""),
        "lsd": ctx.fb_dtsg,
        "__spin_r": "1027694919",
        "__spin_b": "trunk",
        "__spin_t": int(time.time() * 1000),
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "ProfileCometAppCollectionSelfFriendsListRendererPaginationQuery",
        "variables": json.dumps(
            {
                "count": 20,
                "cursor": None,
                "scale": 1,
                "search": search_query.strip(),
                "id": "YXBwX2NvbGxlY3Rpb246cGZiaWQwMkJSM3NDeXRjNkJIeVVXem9OeUxNcjNoYnVDclRFZkdCcVlEaXZuSlZYOUNLR2pXVmRyYTQ4U29FalJTVzduMm03NlhDa0xEQXAybVVUenF6RXZraGc3ZHkyaGw=",
            }
        ),
        "server_timestamps": True,
        "doc_id": "31767020089578751",
    }

    url = "https://www.facebook.com/api/graphql/"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)

    if not res_data or not res_data.get("data"):
        raise Exception("searchFriends returned empty object.")

    if res_data.get("errors"):
        raise Exception(f"searchFriends errors: {res_data['errors']}")

    friends_data = (
        res_data["data"].get("node", {}).get("pageItems", {}).get("edges", [])
    )
    formatted_friends = []

    for edge in friends_data:
        friend = edge.get("node", {})
        friend_user = friend.get("node") or friend

        # Simple extraction of mutual friends count
        mutual_friends = 0
        subtitle = friend.get("subtitle_text", {}).get("text", "")
        import re

        mutual_match = re.search(r"(\d+)\s+mutual\s+friend", subtitle, re.IGNORECASE)
        if mutual_match:
            mutual_friends = int(mutual_match.group(1))

        formatted_friends.append(
            {
                "userID": friend_user.get("id") or friend.get("id"),
                "name": friend.get("title", {}).get("text")
                or friend_user.get("name")
                or friend.get("name"),
                "profilePicture": friend.get("image", {}).get("uri"),
                "profileUrl": friend.get("url") or friend_user.get("url"),
                "subtitle": subtitle,
                "mutualFriends": mutual_friends,
                "friendshipStatus": friend_user.get("friendship_status", "UNKNOWN"),
            }
        )

    return formatted_friends
