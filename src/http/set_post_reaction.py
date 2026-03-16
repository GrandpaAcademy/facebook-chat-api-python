import json
import base64
import random
from typing import Any, Union
from ..utils.utils import parse_and_check_login

async def set_post_reaction(post_func, ctx: Any, post_id: str, type: Union[int, str]):
    reaction_map = {
        "unlike": 0,
        "like": 1,
        "heart": 2,
        "love": 16,
        "haha": 4,
        "wow": 3,
        "sad": 7,
        "angry": 8,
    }

    if isinstance(type, str):
        type = reaction_map.get(type.lower(), 1)
        
    feedback_id = base64.b64encode(f"feedback:{post_id}".encode()).decode()
    
    variables = {
        "input": {
            "actor_id": ctx.user_id,
            "feedback_id": feedback_id,
            "feedback_reaction": type,
            "feedback_source": "OBJECT",
            "is_tracking_encrypted": True,
            "tracking": [],
            "session_id": "f7dd50dd-db6e-4598-8cd9-561d5002b423",
            "client_mutation_id": str(random.randint(0, 19)),
        },
        "useDefaultActor": False,
        "scale": 3,
    }
    
    form = {
        "av": ctx.user_id,
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "CometUFIFeedbackReactMutation",
        "doc_id": "4769042373179384",
        "variables": json.dumps(variables),
    }

    url = "https://www.facebook.com/api/graphql/"
    res = await post_func(url, ctx, form)
    res_data = parse_and_check_login(ctx, res)
    
    if res_data and res_data.get("errors"):
        raise Exception(f"setPostReaction errors: {res_data['errors']}")
        
    try:
        feedback_info = res_data["data"]["feedback_react"]["feedback"]
        return {
            "viewer_feedback_reaction_info": feedback_info.get("viewer_feedback_reaction_info"),
            "supported_reactions": feedback_info.get("supported_reactions"),
            "reaction_count": feedback_info.get("reaction_count"),
        }
    except:
        return res_data
