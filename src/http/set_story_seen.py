import json
import random
import time
import base64
from typing import Any
from ..utils.utils import parse_and_check_login, get_signature_id


async def set_story_seen(post_func, ctx: Any, story_id: str):
    # Extract bucket_id from story_id
    bucket_id = story_id
    if isinstance(story_id, str) and ":" in story_id:
        try:
            decoded = base64.b64decode(story_id).decode("utf-8")
            import re

            match = re.search(r"(\d+)", decoded)
            if match:
                bucket_id = match.group(1)
        except Exception:
            pass

    variables = {
        "input": {
            "bucket_id": bucket_id,
            "story_id": story_id,
            "actor_id": ctx.user_id,
            "client_mutation_id": str(random.randint(1, 16)),
        },
        "scale": 1,
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
        "fb_api_req_friendly_name": "storiesUpdateSeenStateMutation",
        "variables": json.dumps(variables),
        "server_timestamps": True,
        "doc_id": "9567413276713742",
    }

    url = "https://www.facebook.com/api/graphql/"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)

    if res_data and res_data.get("errors"):
        raise Exception(f"setStorySeen errors: {res_data['errors']}")

    return {
        "success": True,
        "story_id": story_id,
        "bucket_id": bucket_id,
        "seen_time": int(time.time() * 1000),
    }
