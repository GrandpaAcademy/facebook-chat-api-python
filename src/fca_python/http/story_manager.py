import json
import random
import time
from typing import Any, Dict
from ..utils.utils import parse_and_check_login, get_signature_id


async def story_manager(post_func, ctx: Any, options: Dict[str, Any]):
    action = options.get("action")
    story_id = options.get("storyID")

    if action == "delete":
        if not story_id:
            raise Exception("Story ID is required for delete action")

        variables = {
            "input": {
                "story_ids": [story_id],
                "actor_id": ctx.user_id,
                "client_mutation_id": str(random.randint(1, 16)),
            },
            "enable_profile_story_consumption": False,
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
            "fb_api_req_friendly_name": "StoriesDeleteCardOptionMenuItem_StoriesDeleteMutation",
            "variables": json.dumps(variables),
            "server_timestamps": True,
            "doc_id": "30236153679305121",
        }

        url = "https://www.facebook.com/api/graphql/"
        res = await post_func(url, ctx, form)
        res_data = parse_and_check_login(ctx, res)

        if res_data and res_data.get("errors"):
            raise Exception(f"storyManager delete errors: {res_data['errors']}")

        return res_data

    elif action == "check":
        variables = {"count": 50, "scale": 1, "id": ctx.user_id}

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
            "fb_api_req_friendly_name": "CometStoriesSuspenseViewerPaginationQuery",
            "variables": json.dumps(variables),
            "server_timestamps": True,
            "doc_id": "7723194127725452",
        }

        url = "https://www.facebook.com/api/graphql/"
        res = await post_func(url, ctx, form)
        res_data = parse_and_check_login(ctx, res)

        stories = []
        try:
            if res_data and res_data.get("data", {}).get("node", {}).get(
                "story_bucket"
            ):
                bucket = res_data["data"]["node"]["story_bucket"]
                for edge in bucket.get("unified_stories", {}).get("edges", []):
                    node = edge.get("node", {})
                    stories.append(
                        {
                            "id": node.get("id"),
                            "creation_time": node.get("creation_time"),
                            "attachments": node.get("attachments", []),
                            "bucket_id": bucket.get("id"),
                        }
                    )
        except Exception:
            pass

        return {"success": True, "stories": stories, "count": len(stories)}

    else:
        raise Exception(f"Action '{action}' not implemented in storyManager")
