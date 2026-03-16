import json
from typing import Any
from ..utils.utils import parse_and_check_login


async def follow(post_func, ctx: Any, sender_id: str, enable: bool):
    if enable:
        form = {
            "av": ctx.user_id,
            "fb_api_req_friendly_name": "CometUserFollowMutation",
            "fb_api_caller_class": "RelayModern",
            "doc_id": "25472099855769847",
            "variables": json.dumps(
                {
                    "input": {
                        "attribution_id_v2": "ProfileCometTimelineListViewRoot.react,comet.profile.timeline.list,via_cold_start,1717249218695,723451,250100865708545,,",
                        "is_tracking_encrypted": True,
                        "subscribe_location": "PROFILE",
                        "subscribee_id": str(sender_id),
                        "tracking": None,
                        "actor_id": ctx.user_id,
                        "client_mutation_id": "1",
                    },
                    "scale": 1,
                }
            ),
        }
    else:
        form = {
            "av": ctx.user_id,
            "fb_api_req_friendly_name": "CometUserUnfollowMutation",
            "fb_api_caller_class": "RelayModern",
            "doc_id": "25472099855769847",  # Note: JS used same doc_id for both? Might be a typo in JS or just how it works.
            "variables": json.dumps(
                {
                    "action_render_location": "WWW_COMET_FRIEND_MENU",
                    "input": {
                        "attribution_id_v2": "ProfileCometTimelineListViewRoot.react,comet.profile.timeline.list,tap_search_bar,1717294006136,602597,250100865708545,,",
                        "is_tracking_encrypted": True,
                        "subscribe_location": "PROFILE",
                        "tracking": None,
                        "unsubscribee_id": str(sender_id),
                        "actor_id": ctx.user_id,
                        "client_mutation_id": "10",
                    },
                    "scale": 1,
                }
            ),
        }

    url = "https://www.facebook.com/api/graphql/"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)

    if res_data and res_data.get("errors"):
        raise Exception(f"follow errors: {res_data['errors']}")

    return res_data
