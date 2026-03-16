import json
import random
from typing import Any
from ..utils.utils import parse_and_check_login

async def change_bio(post_func, ctx: Any, bio: str, publish: bool = False):
    variables = {
        "input": {
            "bio": bio,
            "publish_bio_feed_story": publish,
            "actor_id": ctx.user_id,
            "client_mutation_id": str(random.randint(0, 1024)),
        },
        "hasProfileTileViewID": False,
        "profileTileViewID": None,
        "scale": 1,
    }
    
    form = {
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "ProfileCometSetBioMutation",
        "doc_id": "2725043627607610",
        "variables": json.dumps(variables),
        "av": ctx.user_id,
    }
    
    url = "https://www.facebook.com/api/graphql/"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)
    
    if res_data and res_data.get("errors"):
        raise Exception(f"changeBio errors: {res_data['errors']}")
    return res_data
