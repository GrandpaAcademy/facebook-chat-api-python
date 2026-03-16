import json
import random
from typing import List, Optional
from ..utils.utils import post, parse_and_check_login


async def create_new_group(
    ctx, participant_ids: List[str], group_title: Optional[str] = None
):
    pids = [{"fbid": pid} for pid in participant_ids]
    pids.append({"fbid": ctx.user_id})

    variables = {
        "input": {
            "entry_point": "jewel_new_group",
            "actor_id": ctx.user_id,
            "participants": pids,
            "client_mutation_id": str(random.randint(0, 1024)),
            "thread_settings": {
                "name": group_title,
                "joinable_mode": "PRIVATE",
                "thread_image_fbid": None,
            },
        }
    }

    form = {
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "MessengerGroupCreateMutation",
        "av": ctx.user_id,
        "doc_id": "577041672419534",
        "variables": json.dumps(variables),
    }

    res = await post("https://www.facebook.com/api/graphql/", ctx, form)
    res_data = parse_and_check_login(ctx)(res)

    if "errors" in res_data:
        raise Exception(f"createNewGroup error: {res_data['errors']}")

    try:
        return res_data["data"]["messenger_group_thread_create"]["thread"][
            "thread_key"
        ]["thread_fbid"]
    except KeyError, TypeError:
        raise Exception(f"createNewGroup failed to parse response: {res_data}")
