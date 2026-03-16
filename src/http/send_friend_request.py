import json
import time
import random
from typing import Any
from ..utils.utils import parse_and_check_login, get_signature_id


async def send_friend_request(post_func, ctx: Any, user_id: str):
    variables = {
        "input": {
            "click_correlation_id": str(int(time.time() * 1000)),
            "click_proof_validation_result": '{"validated":true}',
            "friend_requestee_ids": [str(user_id)],
            "friending_channel": "FRIENDS_HOME_MAIN",
            "warn_ack_for_ids": [],
            "actor_id": ctx.user_id,
            "client_mutation_id": str(random.randint(0, 9)),
        },
        "scale": 1,
    }

    form = {
        "av": ctx.user_id,
        "__aaid": 0,
        "__user": ctx.user_id,
        "__a": 1,
        "__req": get_signature_id(),
        "__hs": "20353.HYP:comet_pkg.2.1...0",
        "dpr": 1,
        "__ccg": "EXCELLENT",
        "__rev": "1027405870",
        "__s": get_signature_id(),
        "__hsi": "7552782279085106329",
        "__comet_req": 15,
        "fb_dtsg": ctx.fb_dtsg,
        "jazoest": getattr(ctx, "ttstamp", ""),
        "lsd": ctx.fb_dtsg,
        "__spin_r": "1027405870",
        "__spin_b": "trunk",
        "__spin_t": int(time.time() * 1000),
        "__crn": "comet.fbweb.CometFriendingRoute",
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "FriendingCometFriendRequestSendMutation",
        "variables": json.dumps(variables),
        "server_timestamps": True,
        "doc_id": "24614631718227645",
    }

    url = "https://www.facebook.com/api/graphql/"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)

    if res_data and res_data.get("errors"):
        raise Exception(f"sendFriendRequest errors: {res_data['errors']}")

    if res_data and "data" in res_data and res_data["data"].get("friend_request_send"):
        response_data = res_data["data"]["friend_request_send"]
        if (
            response_data.get("friend_requestees")
            and len(response_data["friend_requestees"]) > 0
        ):
            requestee = response_data["friend_requestees"][0]
            result = {
                "userID": requestee.get("id"),
                "friendshipStatus": requestee.get("friendship_status"),
                "success": requestee.get("friendship_status") == "OUTGOING_REQUEST",
            }
            if requestee.get("profile_action"):
                result["actionTitle"] = (
                    requestee["profile_action"].get("title", {}).get("text", "")
                )
            return result
        else:
            raise Exception("No friend request data received")
    else:
        raise Exception("Invalid response format")
