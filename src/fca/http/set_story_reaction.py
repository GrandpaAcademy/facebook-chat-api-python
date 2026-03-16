import json
import random
import time
from typing import Any, Union
from ..utils.utils import parse_and_check_login, get_signature_id


async def set_story_reaction(
    post_func, ctx: Any, story_id: str, react: Union[int, str]
):
    reaction_map = {
        1: "👍",
        2: "❤️",
        3: "🤗",
        4: "😆",
        5: "😮",
        6: "😢",
        7: "😡",
        "like": "👍",
        "love": "❤️",
        "heart": "❤️",
        "haha": "😆",
        "wow": "😮",
        "sad": "😢",
        "angry": "😡",
    }

    reaction = reaction_map.get(react, react if isinstance(react, str) else "❤️")

    variables = {
        "input": {
            "attribution_id_v2": f"StoriesCometSuspenseRoot.react,comet.stories.viewer,unexpected,{int(time.time()*1000)},356653,,;CometHomeRoot.react,comet.home,tap_tabbar,{int(time.time()*1000)},109945,4748854339,,",
            "lightweight_reaction_actions": {"offsets": [0], "reaction": reaction},
            "message": reaction,
            "story_id": story_id,
            "story_reply_type": "LIGHT_WEIGHT",
            "actor_id": ctx.user_id,
            "client_mutation_id": str(random.randint(1, 16)),
        }
    }

    form = {
        "av": ctx.user_id,
        "__aaid": 0,
        "__user": ctx.user_id,
        "__a": 1,
        "__req": get_signature_id(),
        "__hs": getattr(ctx, "fb_dtsg_ag", ""),
        "dpr": 1,
        "__ccg": "EXCELLENT",
        "__rev": getattr(ctx, "req_id", ""),
        "__s": get_signature_id(),
        "__hsi": getattr(ctx, "hsi", ""),
        "__comet_req": 15,
        "fb_dtsg": ctx.fb_dtsg,
        "jazoest": getattr(ctx, "ttstamp", ""),
        "lsd": ctx.fb_dtsg,
        "__spin_r": getattr(ctx, "req_id", ""),
        "__spin_b": "trunk",
        "__spin_t": int(time.time() * 1000),
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "useStoriesSendReplyMutation",
        "variables": json.dumps(variables),
        "server_timestamps": True,
        "doc_id": "9697491553691692",
    }

    url = "https://www.facebook.com/api/graphql/"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)

    if res_data and res_data.get("errors"):
        raise Exception(f"setStoryReaction errors: {res_data['errors']}")

    return res_data
