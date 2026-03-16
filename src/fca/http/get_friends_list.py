from typing import Any, Dict, List
from ..utils.utils import parse_and_check_login, format_id

GENDERS = {
    0: "unknown",
    1: "female_singular",
    2: "male_singular",
    3: "female_singular_guess",
    4: "male_singular_guess",
    5: "mixed",
    6: "neuter_singular",
    7: "unknown_singular",
    8: "female_plural",
    9: "male_plural",
    10: "neuter_plural",
    11: "unknown_plural",
}


def format_data(obj: Dict[str, Any]) -> List[Dict[str, Any]]:
    results = []
    for key, user in obj.items():
        results.append(
            {
                "alternateName": user.get("alternateName"),
                "firstName": user.get("firstName"),
                "gender": GENDERS.get(user.get("gender", 0)),
                "userID": format_id(str(user.get("id"))),
                "isFriend": bool(user.get("is_friend")),
                "fullName": user.get("name"),
                "profilePicture": user.get("thumbSrc"),
                "type": user.get("type"),
                "profileUrl": user.get("uri"),
                "vanity": user.get("vanity"),
                "isBirthday": bool(user.get("is_birthday")),
            }
        )
    return results


async def get_friends_list(post_func, ctx: Any):
    # Node.js postFormData uses qs for viewer: ctx.userID
    # We'll pass it as part of the URL params in our post_func if we adapt it,
    # or just pass it in the form if the endpoint accepts it there.
    # Actually, let's update our global 'post' in api.py to support params.

    url = "https://www.facebook.com/chat/user_info_all"
    form = {}
    params = {"viewer": ctx.user_id}

    # We call post_func with extra params if supported, or we just handle it here.
    # To keep it simple, we'll use the ctx.client directly or adapt post_func.
    # Our post_func (from api.py) takes (url, ctx, form).

    # Let's use the underlying ctx.client to have full control for this specific case.

    res = await post_func(url, ctx, form, params=params)
    res_data = parse_and_check_login(ctx, res)

    if not res_data:
        raise Exception("getFriendsList returned empty object.")
    if res_data.get("error"):
        raise Exception(f"getFriendsList error: {res_data['error']}")

    return format_data(res_data.get("payload", {}))
