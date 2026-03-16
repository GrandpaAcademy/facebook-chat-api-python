import json
from typing import Any
from ..utils.utils import parse_and_check_login


async def set_message_reaction(
    post_func,
    ctx: Any,
    reaction: str,
    message_id: str,
    force_custom_reaction: bool = False,
):
    # Mapping of common reaction names to emojis (simplified)
    reactions_map = {
        ":heart_eyes:": "😍",
        ":love:": "😍",
        ":laughing:": "😆",
        ":haha:": "😆",
        ":open_mouth:": "😮",
        ":wow:": "😮",
        ":cry:": "😢",
        ":sad:": "😢",
        ":angry:": "😠",
        ":thumbsup:": "👍",
        ":like:": "👍",
        ":thumbsdown:": "👎",
        ":dislike:": "👎",
        ":heart:": "❤️",
        ":glowingheart:": "💗",
    }

    if reaction in reactions_map:
        reaction = reactions_map[reaction]

    variables = {
        "data": {
            "client_mutation_id": ctx.client_mutation_id,
            "actor_id": ctx.user_id,
            "action": "REMOVE_REACTION" if reaction == "" else "ADD_REACTION",
            "message_id": message_id,
            "reaction": reaction,
        },
    }
    ctx.client_mutation_id += 1

    qs = {
        "doc_id": "1491398900900362",
        "variables": json.dumps(variables),
        "dpr": 1,
    }

    res = await post_func(
        "https://www.facebook.com/webgraphql/mutation/", ctx, {}, params=qs
    )
    res_data = parse_and_check_login(ctx, res)
    if not res_data:
        raise Exception("setReaction returned empty object.")
    if res_data.get("error"):
        raise Exception(f"setReaction error: {res_data['error']}")
    return res_data
